import os
import ftplib
import argparse
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


load_dotenv()

def download_images(csv_path, ftp_host, ftp_user, ftp_password, ftp_base_path, output_dir, label, max_images, num_threads=8):
    """
    Downloads images for a specific label from an FTP server based on a CSV file.
    Credentials and paths are taken from environment variables or arguments.
    Uses pandas for CSV handling and multithreaded downloads.
    """

    if not ftp_host:
        print("Error: FTP host is required. Set FTP_HOST environment variable or use --ftp-host argument.")
        return
    if not ftp_user:
        print("Error: FTP user is required. Set FTP_USER environment variable or use --ftp-user argument.")
        return
    if not ftp_password:
        print("Error: FTP password is required. Set FTP_PASSWORD environment variable.")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_path.resolve()}")
    # --- Read CSV and filter with pandas ---
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_path}'")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    if 'class' not in df.columns or 'filename' not in df.columns:
        print(f"Error: CSV file '{csv_path}' must contain 'class' and 'filename' columns.")
        return

    filtered_df = df[df['class'] == label]
    unique_filenames = filtered_df['filename'].drop_duplicates().tolist()
    image_paths_to_download = unique_filenames[:max_images]

    if not image_paths_to_download:
        print(f"No images found for label '{label}' in '{csv_path}'.")
        return

    print(f"Found {len(image_paths_to_download)} images for label '{label}'. Attempting download...")

    # Remove files that already exist locally
    image_paths_to_download = [f for f in image_paths_to_download if not (output_path / Path(f).name).exists()]
    if not image_paths_to_download:
        print("All images already downloaded.")
        return

    print(f"{len(image_paths_to_download)} images to download after removing already downloaded files.")

    # current_base_path = ftp_base_path if ftp_base_path else ""
    # if current_base_path and not current_base_path.endswith('/'):
    #     current_base_path += '/'
    current_base_path = "/SlidingWindow/train/"  # add path
    if ftp_base_path:
        current_base_path = ftp_base_path
        if not current_base_path.endswith('/'):
            current_base_path += '/'

    # Split the list into batches for each thread
    def chunkify(lst, n):
        return [lst[i::n] for i in range(n)]

    batches = chunkify(image_paths_to_download, num_threads)

    def download_batch(batch):
        results = []
        try:
            with ftplib.FTP(ftp_host) as ftp:
                ftp.login(user=ftp_user, passwd=ftp_password)
                for relative_image_path in batch:
                    clean_relative_path = relative_image_path.lstrip('/')
                    ftp_full_path = current_base_path + clean_relative_path
                    local_file_name = Path(clean_relative_path).name
                    local_full_path = output_path / local_file_name
                    try:
                        with open(local_full_path, 'wb') as fp:
                            ftp.retrbinary(f'RETR {ftp_full_path}', fp.write)
                        results.append((relative_image_path, True, None))
                    except ftplib.error_perm as e:
                        results.append((relative_image_path, False, f"FTP Error (permission/not found?): {e}"))
                    except Exception as e:
                        results.append((relative_image_path, False, f"Error: {e}"))
        except Exception as e:
            for relative_image_path in batch:
                results.append((relative_image_path, False, f"Batch FTP connection error: {e}"))
        return results

    downloaded_count = 0
    errors = []
    successfully_downloaded_paths = []

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(download_batch, batch): batch for batch in batches if batch}
        for f in tqdm(as_completed(futures), total=len(futures), desc=f"Downloading {label} images", unit="batch"):
            batch_results = f.result()
            for original_path, success, error_msg in batch_results:
                if success:
                    downloaded_count += 1
                    successfully_downloaded_paths.append(original_path)
                else:
                    failed_filename = Path(original_path.lstrip('/')).name if original_path else "Unknown file"
                    tqdm.write(f"Failed to download {failed_filename}: {error_msg}")
                    errors.append((failed_filename, error_msg))

    print(f"\nDownload attempt finished. Successfully downloaded {downloaded_count} new images.")
    if errors:
        print(f"{len(errors)} files failed to download.")

    if successfully_downloaded_paths:
        downloaded_rows_df = filtered_df[filtered_df['filename'].isin(successfully_downloaded_paths)]
        log_file_path = output_path / "downloaded_log.csv"
        try:
            downloaded_rows_df.to_csv(log_file_path, index=False)
            print(f"Successfully saved download log to: {log_file_path}")
        except Exception as e:
            print(f"Error saving download log: {e}")
    elif downloaded_count == 0:
        print("No images were downloaded, so no log file was created.")

def estimate_download_size(filenames, ftp_host, ftp_user, ftp_password, ftp_base_path):
    total_bytes = 0
    missing = 0
    try:
        with ftplib.FTP(ftp_host) as ftp:
            ftp.login(user=ftp_user, passwd=ftp_password)
            base_path = ftp_base_path if ftp_base_path else ""
            if base_path and not base_path.endswith('/'):
                base_path += '/'
            for fname in tqdm(filenames, desc="Estimating size", unit="file"):
                ftp_path = base_path + fname.lstrip('/')
                try:
                    size = ftp.size(ftp_path)
                    if size:
                        total_bytes += size
                except Exception:
                    missing += 1
    except Exception as e:
        print(f"FTP error during size estimation: {e}")
        return None, None
    return total_bytes, missing

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download specific images from FTP based on CSV labels. Reads FTP credentials and base path from .env file by default, but can be overridden by arguments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--csv-path", required=False, help="Path to the training CSV file.")
    parser.add_argument("--output-dir", default="images_ignore/damage_type_images", help="Local directory to save downloaded images.")
    parser.add_argument("--label", default=None, help="Label to filter images by (German name from README).")
    parser.add_argument("--max-images", type=int, default=100, help="Maximum number of images to download.")
    parser.add_argument("--num-threads", type=int, default=8, help="Number of threads for parallel download.")

    parser.add_argument("--ftp-host", default=os.getenv("FTP_HOST"), help="FTP server hostname (overrides FTP_HOST in .env)")
    parser.add_argument("--ftp-user", default=os.getenv("FTP_USER"), help="FTP username (overrides FTP_USER in .env)")
    parser.add_argument("--ftp-base-path", default=os.getenv("FTP_BASE_PATH", ""), help="Base directory path on FTP server (overrides FTP_BASE_PATH in .env)")

    args = parser.parse_args()

    ftp_password = os.getenv("FTP_PASSWORD")

    # Interactive TUI for missing params
    def prompt_if_missing(val, prompt, is_password=False):
        if val:
            return val
        if is_password:
            import getpass
            return getpass.getpass(prompt)
        return input(prompt)

    args.csv_path = prompt_if_missing(args.csv_path, "Enter path to CSV file: ")
    args.ftp_host = prompt_if_missing(args.ftp_host, "Enter FTP host: ")
    args.ftp_user = prompt_if_missing(args.ftp_user, "Enter FTP user: ")
    ftp_password = prompt_if_missing(ftp_password, "Enter FTP password: ", is_password=True)
    args.label = prompt_if_missing(args.label, "Enter label to filter images by: ")

    # --- Load CSV for stats preview ---
    try:
        df = pd.read_csv(args.csv_path, encoding='utf-8')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit(1)
    if 'class' not in df.columns or 'filename' not in df.columns:
        print(f"Error: CSV file '{args.csv_path}' must contain 'class' and 'filename' columns.")
        exit(1)

    def show_label_stats(label):
        filtered = df[df['class'] == label]
        count = len(filtered)
        print(f"\n--- Stats for label '{label}' ---")
        print(f"Number of images: {count}")
        if count > 0:
            print("Sample filenames:")
            for fname in filtered['filename'].head(5):
                print(f"  - {fname}")
        print("-----------------------------\n")
        return count

    # TUI loop for stats and confirmation
    while True:
        show_label_stats(args.label)
        print("Options:")
        print("  [1] Show stats for a different label")
        print("  [2] Set number of images to download (current: {} )".format(args.max_images))
        print("  [3] Estimate total download size")
        print("  [4] Proceed with download")
        print("  [5] Exit")
        choice = input("Choose an option [4]: ").strip()
        if choice == "1":
            new_label = input("Enter new label: ").strip()
            if new_label:
                args.label = new_label
        elif choice == "2":
            try:
                new_max = int(input("Enter number of images to download: ").strip())
                if new_max > 0:
                    args.max_images = new_max
            except Exception:
                print("Invalid number.")
        elif choice == "3":
            filtered = df[df['class'] == args.label]
            unique_filenames = filtered['filename'].drop_duplicates().tolist()[:args.max_images]
            print("Estimating total download size for {} images...".format(len(unique_filenames)))
            total_bytes, missing = estimate_download_size(unique_filenames, args.ftp_host, args.ftp_user, ftp_password, args.ftp_base_path)
            if total_bytes is not None:
                mb = total_bytes / (1024*1024)
                gb = mb / 1024
                print(f"Estimated total size: {mb:.2f} MB ({gb:.2f} GB)")
                if missing:
                    print(f"Warning: {missing} files could not be sized (may not exist or permission denied)")
            else:
                print("Could not estimate size.")
        elif choice == "5":
            print("Aborted by user.")
            exit(0)
        else:
            break


    if not parser.get_default('output_dir') == args.output_dir and args.output_dir:
        pass
    else:
        # Set output-dir to images_ignore/<label>
        args.output_dir = f"images_ignore/{args.label}"
        print(f"Output directory set to: {args.output_dir}")

    # Show summary and confirm
    print("\n===== Download Configuration =====")
    print(f"CSV Path      : {args.csv_path}")
    print(f"Output Dir    : {args.output_dir}")
    print(f"Label         : {args.label}")
    print(f"Max Images    : {args.max_images}")
    print(f"Num Threads   : {args.num_threads}")
    print(f"FTP Host      : {args.ftp_host}")
    print(f"FTP User      : {args.ftp_user}")
    print(f"FTP Base Path : {args.ftp_base_path}")
    print("==================================")

    # FTP base path bugfix for windows git bash
    if args.ftp_base_path and args.ftp_base_path.startswith('C:/Program Files/Git/'):
        original_ftp_path_candidate = args.ftp_base_path.replace('C:/Program Files/Git', '')
        if not original_ftp_path_candidate.startswith('/'):
            original_ftp_path_candidate = '/' + original_ftp_path_candidate
        print(f"NOTICE: FTP Base Path from environment was '{args.ftp_base_path}'.")
        args.ftp_base_path = original_ftp_path_candidate
        print(f"Corrected FTP Base Path for download operations to: {args.ftp_base_path}")

    proceed = input("Proceed with download? [Y/n]: ").strip().lower()
    if proceed not in ("", "y", "yes"):
        print("Aborted by user.")
        exit(0)

    print("Starting image extraction process...")
    download_images(
        csv_path=args.csv_path,
        ftp_host=args.ftp_host,
        ftp_user=args.ftp_user,
        ftp_password=ftp_password,
        ftp_base_path=args.ftp_base_path,
        output_dir=args.output_dir,
        label=args.label,
        max_images=args.max_images,
        num_threads=args.num_threads
    )
    print("Image extraction process finished.")
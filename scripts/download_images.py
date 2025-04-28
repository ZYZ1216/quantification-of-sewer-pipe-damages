import csv
import os
import ftplib
import argparse
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm


load_dotenv()

def download_images(csv_path, ftp_host, ftp_user, ftp_password, ftp_base_path, output_dir, label, max_images):
    """
    Downloads images for a specific label from an FTP server based on a CSV file.
    Credentials and paths are taken from environment variables or arguments.
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

    # --- Read CSV and filter ---
    image_paths_to_download = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'class' not in reader.fieldnames or 'filename' not in reader.fieldnames:
                print(f"Error: CSV file '{csv_path}' must contain 'class' and 'filename' columns.")
                return
            
            count = 0
            for row in reader:
                if row['class'] == label:
                    image_paths_to_download.append(row['filename'])
                    count += 1
                    if count >= max_images:
                        break
    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_path}'")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    if not image_paths_to_download:
        print(f"No images found for label '{label}' in '{csv_path}'.")
        return

    print(f"Found {len(image_paths_to_download)} images for label '{label}'. Attempting download...")

    # --- Connect to FTP and download ---
    downloaded_count = 0
    try:
        with ftplib.FTP(ftp_host) as ftp:
            print(f"Attempting to connect to FTP host: {ftp_host} with user: {ftp_user}")
            ftp.login(user=ftp_user, passwd=ftp_password)
            print(f"Successfully connected and logged in.")
            
            current_base_path = ftp_base_path if ftp_base_path else ""
            if current_base_path and not current_base_path.endswith('/'):
                current_base_path += '/'

            # Wrap the loop with tqdm for progress bar
            pbar = tqdm(image_paths_to_download, desc=f"Downloading {label} images", unit="file")
            for relative_image_path in pbar:
                clean_relative_path = relative_image_path.lstrip('/')
                ftp_full_path = current_base_path + clean_relative_path
                local_file_name = Path(clean_relative_path).name
                local_full_path = output_path / local_file_name

                # Update progress bar description with current file
                pbar.set_postfix_str(local_file_name, refresh=True)

                if local_full_path.exists():
                    # Use tqdm.write to print messages without breaking the bar
                    # tqdm.write(f"Skipping already downloaded file: {local_file_name}")
                    # Skip updating downloaded_count here, let tqdm handle the iteration count
                    continue

                # print(f"Attempting to download: {ftp_full_path} -> {local_full_path}") # Optional: Keep if needed, but tqdm provides progress
                try:
                    # Retrieve file size for potential progress within file download (optional)
                    # file_size = ftp.size(ftp_full_path)
                    # if file_size:
                    #     pbar_file = tqdm(total=file_size, unit='B', unit_scale=True, desc=local_file_name, leave=False)

                    with open(local_full_path, 'wb') as fp:
                        # Simple download without inner progress bar
                        ftp.retrbinary(f'RETR {ftp_full_path}', fp.write)

                        # Example with inner progress bar (uncomment above and use callback)
                        # ftp.retrbinary(f'RETR {ftp_full_path}', lambda data: (fp.write(data), pbar_file.update(len(data))))

                    # pbar_file.close() # Close inner progress bar if used
                    downloaded_count += 1 # Increment only on successful download
                    # tqdm.write(f"Successfully downloaded: {local_file_name}") # Optional: Keep if needed
                except ftplib.error_perm as e:
                    tqdm.write(f"FTP Error (permission/not found?) for {ftp_full_path}: {e}")
                except Exception as e:
                    tqdm.write(f"Error downloading {ftp_full_path}: {e}")
            
            pbar.close() # Close the main progress bar

    except ftplib.all_errors as e:
        print(f"\nFTP connection or login error: {e}") # Add newline to avoid overlapping with pbar
        return
    except Exception as e:
        print(f"An unexpected error occurred during FTP operations: {e}")
        return

    print(f"\nDownload attempt finished. Successfully downloaded {downloaded_count} new images." )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download specific images from FTP based on CSV labels. Reads FTP credentials and base path from .env file by default, but can be overridden by arguments.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--csv-path", required=True, help="Path to the training CSV file.")
    parser.add_argument("--output-dir", default="images_ignore/damage_type_images", help="Local directory to save downloaded images.")
    parser.add_argument("--label", default="Hindernis", help="Label to filter images by (German name from README).")
    parser.add_argument("--max-images", type=int, default=100, help="Maximum number of images to download.")

    parser.add_argument("--ftp-host", default=os.getenv("FTP_HOST"), help="FTP server hostname (overrides FTP_HOST in .env)")
    parser.add_argument("--ftp-user", default=os.getenv("FTP_USER"), help="FTP username (overrides FTP_USER in .env)")
    parser.add_argument("--ftp-base-path", default=os.getenv("FTP_BASE_PATH", ""), help="Base directory path on FTP server (overrides FTP_BASE_PATH in .env)")

    args = parser.parse_args()

    ftp_password = os.getenv("FTP_PASSWORD")

    print("Starting image extraction process...")
    download_images(
        csv_path=args.csv_path,
        ftp_host=args.ftp_host,
        ftp_user=args.ftp_user,
        ftp_password=ftp_password,
        ftp_base_path=args.ftp_base_path,
        output_dir=args.output_dir,
        label=args.label,
        max_images=args.max_images
    )
    print("Image extraction process finished.") 
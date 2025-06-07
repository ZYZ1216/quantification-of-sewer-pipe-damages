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
    Skips files already downloaded (recorded in .downloaded.log).
    """
    # --- Validate FTP credentials ---
    if not ftp_host:
        print("Error: FTP host is required. Set FTP_HOST environment variable or use --ftp-host argument.")
        return
    if not ftp_user:
        print("Error: FTP user is required. Set FTP_USER environment variable or use --ftp-user argument.")
        return
    if not ftp_password:
        print("Error: FTP password is required. Set FTP_PASSWORD environment variable.")
        return

    # --- Prepare output directory ---
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_path.resolve()}")

    # --- Load already downloaded files ---
    downloaded_log = output_path / ".downloaded.log"
    downloaded_files = set()
    if downloaded_log.exists():
        with open(downloaded_log, "r") as f:
            downloaded_files = set(line.strip() for line in f if line.strip())

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
                    file_name = Path(row['filename'].lstrip('/')).name
                    if file_name not in downloaded_files:  # Skip already recorded files
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
        print(f"No new images found for label '{label}' in '{csv_path}'.")
        return

    print(f"Found {len(image_paths_to_download)} new images for label '{label}'. Attempting download...")

    # --- Connect to FTP and download ---
    downloaded_count = 0
    try:
        with ftplib.FTP(ftp_host) as ftp:
            print(f"Connecting to FTP: {ftp_host} as {ftp_user}...")
            ftp.login(user=ftp_user, passwd=ftp_password)
            print("FTP login successful.")

            current_base_path = ftp_base_path if ftp_base_path else ""
            if current_base_path and not current_base_path.endswith('/'):
                current_base_path += '/'

            # Download with progress bar
            with tqdm(image_paths_to_download, desc=f"Downloading {label}", unit="file") as pbar:
                for relative_image_path in pbar:
                    clean_relative_path = relative_image_path.lstrip('/')
                    ftp_full_path = current_base_path + clean_relative_path
                    local_file_name = Path(clean_relative_path).name
                    local_full_path = output_path / local_file_name

                    pbar.set_postfix(file=local_file_name[:20])  # Show filename in progress bar

                    try:
                        with open(local_full_path, 'wb') as fp:
                            ftp.retrbinary(f'RETR {ftp_full_path}', fp.write)

                        # Record successful download
                        with open(downloaded_log, "a") as f:
                            f.write(f"{local_file_name}\n")
                        downloaded_count += 1

                    except ftplib.error_perm as e:
                        tqdm.write(f"FTP Error for {ftp_full_path}: {e}")
                    except Exception as e:
                        tqdm.write(f"Error downloading {local_file_name}: {e}")

    except ftplib.all_errors as e:
        print(f"\nFTP connection error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print(f"\nDownload complete. New files downloaded: {downloaded_count}/{len(image_paths_to_download)}")
    print(f"Total downloaded files recorded: {len(downloaded_files) + downloaded_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download images from FTP with duplicate prevention.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # 移除 required=True
    parser.add_argument("--csv-path", help="Path to CSV file.")  # 不再是必须参数
    parser.add_argument("--output-dir", default="images_ignore/damage_type_images", help="Output directory.")
    parser.add_argument("--label", default="Hindernis", help="Label to filter by.")
    parser.add_argument("--max-images", type=int, default=100, help="Max images to download.")

    parser.add_argument("--ftp-host", default=os.getenv("FTP_HOST"), help="FTP host (default from .env).")
    parser.add_argument("--ftp-user", default=os.getenv("FTP_USER"), help="FTP user (default from .env).")
    parser.add_argument("--ftp-base-path", default=os.getenv("FTP_BASE_PATH", ""),
                        help="FTP base path (default from .env).")

    args = parser.parse_args()

    download_images(
        csv_path="D:\\Desktop\\THD\\4class\\6th\\ai_project\\quantification-of-sewer-pipe-damages\\data\\train.csv",
        ftp_host=args.ftp_host,
        ftp_user=args.ftp_user,
        ftp_password=os.getenv("FTP_PASSWORD"),
        ftp_base_path=args.ftp_base_path,
        output_dir=args.output_dir,
        label="Muffenschaden",
        max_images=100
    )
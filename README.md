
Main Client Gallery - Production Build (Port 3034)

Mounts:

/mnt/apps/mainclientgallery -> /app/data
/mnt/nextcloud/mainclientgalleryfiles -> /app/storage

Limits:
Main gallery cap: 40GB
Guest upload cap: 1GB

Required Folder Structure Example:

Emma & Josh 22.01.26/
    Wedding Images/
    Video/
    Guest Uploads/
    Selfie Booth/

Deploy with:
docker-compose up --build -d

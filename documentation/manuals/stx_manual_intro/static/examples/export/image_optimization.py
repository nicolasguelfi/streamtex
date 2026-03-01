# Large images slow down export
st_image("huge_photo.png")  # ~5MB when embedded

# Smaller images are better
st_image("icon.png")  # ~50KB when embedded

# Use image compression:
# - JPG for photos (lossy, smaller)
# - PNG for graphics (lossless)
# - WebP for web (best compression, but less supported)

# Recommendation: Keep images < 500KB before export

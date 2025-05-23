import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import piexif
from datetime import datetime

# --------------------- EXIF FUNCTIONS ---------------------
def get_exif_data(image_path):
    try:
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info.get('exif', b''))
        return exif_dict
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load EXIF data:\n{e}")
        return {}

def get_date_taken(exif):
    date_str = exif['0th'].get(piexif.ImageIFD.DateTime)
    if date_str:
        return datetime.strptime(date_str.decode(), '%Y:%m:%d %H:%M:%S')
    return None

def get_camera_make_model(exif):
    make = exif['0th'].get(piexif.ImageIFD.Make)
    model = exif['0th'].get(piexif.ImageIFD.Model)
    return (make.decode() if make else None, model.decode() if model else None)

def get_shutter_speed(exif):
    exposure = exif['Exif'].get(piexif.ExifIFD.ExposureTime)
    if exposure:
        return f"{exposure[0]}/{exposure[1]} sec"
    return None

def get_aperture(exif):
    aperture = exif['Exif'].get(piexif.ExifIFD.FNumber)
    if aperture:
        return round(aperture[0] / aperture[1], 2)
    return None

def get_iso(exif):
    return exif['Exif'].get(piexif.ExifIFD.ISOSpeedRatings)

def get_focal_length(exif):
    focal = exif['Exif'].get(piexif.ExifIFD.FocalLength)
    if focal:
        return round(focal[0] / focal[1], 2)
    return None

def get_flash_status(exif):
    flash = exif['Exif'].get(piexif.ExifIFD.Flash)
    if flash is not None:
        return "Flash fired" if (flash & 1) else "Flash did not fire"
    return None

def get_gps_coords(exif):
    gps_ifd = exif.get('GPS')
    if not gps_ifd:
        return None
    def convert_to_degrees(value):
        d, m, s = value
        return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600
    try:
        lat = convert_to_degrees(gps_ifd.get(piexif.GPSIFD.GPSLatitude))
        lat_ref = gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef).decode()
        lon = convert_to_degrees(gps_ifd.get(piexif.GPSIFD.GPSLongitude))
        lon_ref = gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef).decode()
        if lat_ref != 'N':
            lat = -lat
        if lon_ref != 'E':
            lon = -lon
        return (lat, lon)
    except:
        return None

# --------------------- GUI LOGIC ---------------------
def select_image():
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.webp")]
    )
    if not file_path:
        return

    exif = get_exif_data(file_path)
    if not exif:
        return

    make, model = get_camera_make_model(exif)
    output = f"📷 Camera Make: {make}\n📸 Camera Model: {model}\n"
    output += f"📅 Date Taken: {get_date_taken(exif)}\n"
    output += f"⏱️ Shutter Speed: {get_shutter_speed(exif)}\n"
    output += f"🔆 Aperture (f): {get_aperture(exif)}\n"
    output += f"🎚️ ISO: {get_iso(exif)}\n"
    output += f"🔍 Focal Length: {get_focal_length(exif)} mm\n"
    output += f"💡 Flash: {get_flash_status(exif)}\n"
    gps = get_gps_coords(exif)
    output += f"📍 GPS Coordinates: {gps if gps else 'Not Available'}\n"

    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, output)
    result_text.config(state='disabled')

# --------------------- GUI SETUP ---------------------
root = tk.Tk()
root.title("EXIF Metadata Reader")
root.geometry("600x400")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

select_button = tk.Button(frame, text="📂 Select Image", command=select_image, font=("Arial", 12))
select_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(frame, width=70, height=20, font=("Courier", 10))
result_text.pack()
result_text.config(state='disabled')

root.mainloop()
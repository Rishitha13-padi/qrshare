import os
import threading
from flask import Flask, send_from_directory, abort, render_template_string, request
import qrcode
import socket
import tkinter as tk
from PIL import Image, ImageTk

# Flask app setup
flask_app = Flask(__name__)
DIRECTORY_PATH = "D:/RECENTS/MY STUFF"

# Mapping of file extensions to Font Awesome icons
ICON_MAPPING = {
    'pdf': 'fa-file-pdf',
    'txt': 'fa-file-alt',
    'doc': 'fa-file-word',
    'docx': 'fa-file-word',
    'xls': 'fa-file-excel',
    'xlsx': 'fa-file-excel',
    'ppt': 'fa-file-powerpoint',
    'pptx': 'fa-file-powerpoint',
    'jpg': 'fa-file-image',
    'jpeg': 'fa-file-image',
    'png': 'fa-file-image',
    'gif': 'fa-file-image',
    'zip': 'fa-file-archive',
    'rar': 'fa-file-archive',
    'mp3': 'fa-file-audio',
    'wav': 'fa-file-audio',
    'mp4': 'fa-file-video',
    'avi': 'fa-file-video',
    'mkv': 'fa-file-video',
    'mov': 'fa-file-video',
    'folder': 'fa-folder',
    'default': 'fa-file'
}

def get_file_icon(file_extension):
    return ICON_MAPPING.get(file_extension, ICON_MAPPING['default'])

@flask_app.route('/', methods=['GET', 'POST'])
def list_files():
    try:
        search_query = request.form.get('search', '').lower()
        entries = os.listdir(DIRECTORY_PATH)
        files = [f for f in entries if os.path.isfile(os.path.join(DIRECTORY_PATH, f))]
        folders = [f for f in entries if os.path.isdir(os.path.join(DIRECTORY_PATH, f))]

        if search_query:
            files = [f for f in files if search_query in f.lower()]
            folders = [f for f in folders if search_query in f.lower()]

        entries_html = render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File List</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f2f5;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }
                .container {
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #fff;
                    box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                    animation: fadeIn 1s ease-in-out;
                }
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                h2 {
                    text-align: center;
                    color: #444;
                    margin-bottom: 20px;
                    animation: fadeIn 1s ease-in-out;
                }
                form {
                    text-align: center;
                    margin-bottom: 20px;
                    animation: fadeIn 1s ease-in-out;
                }
                input[type="text"] {
                    padding: 10px;
                    width: 80%;
                    max-width: 400px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin-right: 10px;
                    transition: border-color 0.3s ease;
                }
                input[type="text"]:focus {
                    border-color: #007bff;
                }
                input[type="submit"] {
                    padding: 10px 20px;
                    border: none;
                    background-color: #007bff;
                    color: white;
                    border-radius: 4px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
                ul {
                    list-style: none;
                    padding: 0;
                }
                li {
                    margin: 10px 0;
                    display: flex;
                    align-items: center;
                    animation: fadeIn 1s ease-in-out;
                }
                a {
                    text-decoration: none;
                    color: #007bff;
                    transition: color 0.3s ease;
                    margin-left: 10px;
                }
                a:hover {
                    color: #0056b3;
                }
                .icon {
                    width: 20px;
                    text-align: center;
                    transition: transform 0.3s ease;
                }
                li:hover .icon {
                    transform: scale(1.2);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Files and Folders in Directory</h2>
                <form method="POST">
    <div style="display: flex; align-items: center;">
        <input type="text" name="search" placeholder="Search files and folders" style="flex: 1; padding: 10px; width: 80%; max-width: 400px; border: 1px solid #ddd; border-radius: 4px; margin-right: 10px; transition: border-color 0.3s ease;">
        <button type="submit" style="border: none; background-color: transparent; cursor: pointer;">
            <i class="fas fa-search" style="color: #007bff; font-size: 18px;"></i>
        </button>
    </div>
</form>

                <ul>
                    {% for folder in folders %}
                    <li><i class="fas {{ get_file_icon('folder') }} icon"></i><a href="{{ url_for('list_files') }}">{{ folder }}</a></li>
                    {% endfor %}
                    {% for file in files %}
                    <li><i class="fas {{ get_file_icon(file.split('.')[-1].lower()) }} icon"></i><a href="{{ url_for('download_file', filename=file) }}">{{ file }}</a></li>
                    {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        ''', files=files, folders=folders, get_file_icon=get_file_icon)
        return entries_html
    except Exception as e:
        return str(e)


@flask_app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_from_directory(DIRECTORY_PATH, filename, as_attachment=True)
    except FileNotFoundError:
        return abort(404)


def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((300, 300), Image.LANCZOS)  # High-quality filtering

    return img


def start_flask_app():
    flask_app.run(host='0.0.0.0', port=5000)


# GUI setup
class FileShareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Share App")

        self.label = tk.Label(root, text="Scan the QR code to access the files")
        self.label.pack(pady=10)

        self.canvas = tk.Canvas(root, width=300, height=300)
        self.canvas.pack()

        self.start_server_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_server_button.pack(pady=10)

        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.pack(pady=10)

    def start_server(self):
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        port = 5000
        base_url = f"http://{local_ip}:{port}/"

        # Generate QR code
        img = generate_qr_code(base_url)
        self.qr_img = ImageTk.PhotoImage(img)

        # Clear existing image (optional)
        self.canvas.delete("all")

        # Display QR code on canvas
        self.canvas.create_image(150, 150, image=self.qr_img)

        # Start Flask server in a separate thread
        threading.Thread(target=start_flask_app).start()

    def run_app(self):
        self.root.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    app = FileShareApp(root)
    app.run_app()  # Call the new method to start the GUI application

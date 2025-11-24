import base64

from pathlib import Path

def grab_screenshot(scope, filename="screenshot.png"):

    # Where tm_devices will temporarily store the file
    local_folder = str(Path(".").resolve())

    # Folder on the oscilloscope
    device_folder = "temp"

    scope.save_screenshot(
        "example.jpg",
        colors="INVERTED",
        local_folder=local_folder,
        device_folder=device_folder,
        keep_device_file=True,
    )


from tm_devices import DeviceManager

def main():
    dm = DeviceManager()
    scope = dm.add_scope("TCPIP::10.59.133.248::INSTR", alias="SCOPE1")

    print("Connected:", scope.query("*IDN?"))

    grab_screenshot(scope)

if __name__ == "__main__":
    main()
import time

from calibration.CalibrationSession import CalibrationSession
from config.CalibrationConfig import CalibrationConfigLoader
from config.NTConfig import generate_default
from pipeline.Camera import Camera

FRAMES = 10

if __name__ == "__main__":
    nt_config = generate_default()
    calibration_config_loader = CalibrationConfigLoader()
    calibration_session = CalibrationSession(12, 9, 0.030, 0.023)
    camera = Camera()

    print("Running calibration")

    for i in range(FRAMES):
        print("Caputuring frame in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)

        cam_success, capture = camera.read(nt_config)
        if not cam_success:
            continue

        calibration_session.intake_frame(capture, True)

        print("Captured frame " + str(i) + "/" + str(FRAMES))
        time.sleep(1)

    print("Finished gathering frames")
    calibration_session.save_to_file(calibration_config_loader)

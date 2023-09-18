import cv2

from calibration.CalibrationSession import CalibrationSession
from config.CalibrationConfig import CalibrationConfigLoader

CHARUCO_BOARD_FILENAME = "charuco_board.png"

if __name__ == "__main__":
    calibration_config_loader = CalibrationConfigLoader()
    calibration_session = CalibrationSession()
    print("Running fake calibration")
    image = cv2.imread(CHARUCO_BOARD_FILENAME)
    calibration_session.intake_frame(image, True)
    calibration_session.save_to_file(calibration_config_loader)

import cv2
from pathlib import Path


def grid_the_picture():
    # Load img
    img_path = Path.cwd() / "sc2_maps_images/Abyssal_Reef_LE.jpg"
    print(img_path.is_file())
    print(img_path)
    image = cv2.imread(img_path.__str__())

    # Get data about img
    height = image.shape[0]
    width = image.shape[1]
    print(f"{width=} {height=}")

    x_offset = 2.8
    y_offset = 1.1

    # Work on img
    bases_loc = [(70.5, 117.5), (129.5, 49.5), (42.5, 93.5)]
    # bases_loc = [(38, 122)]

    for point in bases_loc:
        print(height)
        # x line
        p1 = (int(point[0] * x_offset), 0)
        p2 = (int(point[0] * x_offset), height)
        print(f"{p1=} {p2=}")
        cv2.line(image, p1, p2, (0, 0, 255), 5)
        # y line
        p1 = (0, int(point[1] * y_offset))
        p2 = (width, int(point[1] * y_offset))
        print(f"{p1=} {p2=}")
        cv2.line(image, p1, p2, (0, 0, 255), 5)

    # cv2.line(image, (0, 0), (width, height), (0, 0, 255), 2)

    cv2.imshow("Result: ", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # save img
    # parent_file = img_path.parent / "Abyssal_Reef_LE_gridded.jpg"
    # cv2.imwrite(parent_file.__str__(), image, [cv2.IMWRITE_JPEG_QUALITY, 50])


if __name__ == "__main__":
    # grid_the_picture()

    l = [(70.5, 117.5), (129.5, 49.5), (42.5, 93.5), (157.5, 50.5), (58.5, 78.5), (141.5, 65.5), (40.5, 44.5),
         (159.5, 99.5), (100.5, 28.5), (99.5, 115.5), (128.5, 127.5), (71.5, 16.5), (70.5, 94.5), (129.5, 26.5),
         (38.5, 122.5), (161.5, 21.5)]


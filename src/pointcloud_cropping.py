'''
    Here you perform a 3D qutomqtic cropping. The idea is to automatically extract the object of interst in the pointcloud
    To do that I use the fact that the ooi has at least most of its points in every images of the SfM
        So I reproject the pointcloud every frame of the SfM and save the points that are, in every reprojection, within the dimensions of the images
        This suppresses already many points of the background
'''
from automatic_cropping_n_resize import *

class Point:
    def __init__(self, x=0, y=0, z=0, score=0):
        self.x = x
        self.y = y
        self.z = z
        self.score = score

    def __repr__(self):
        return "({}, {}, {}, {})".format(self.x, self.y, self.z, self.score)

def read_pointcloud(treshold=102):
    pc_dir = os.path.join(INPUT_DIR, '../output/OpenMVG/reconstruction_sequential')

    Cropper = automatic_cropator()
    Cropper.INPUT_DIR = os.path.join(INPUT_DIR, '../images_SfM')
    Cropper.OOI_DIR = pc_dir
    Cropper.load_variables(obj_base_name='robust')

    points = []
    for point in Cropper.PC:
        points.append(Point(point[0], point[1], point[2]))

    images = os.listdir(Cropper.INPUT_DIR)
    image_sample = cv2.imread(os.path.join(Cropper.INPUT_DIR, images[0]))
    height, width, channels = image_sample.shape

    print('Extracting the object of interest pointcloud')
    for image_name in images:
        points_projected = Cropper.search_bb(image_name, False)
        for i in range(len(points_projected)):
            if (0<=points_projected[i][0]<=width) and (0<=points_projected[i][1]<=height):
                points[i].score += 1

    selected_points = [[pt.x, pt.y, pt.z] for pt in points if pt.score>=treshold]
    mean_x = sum([pt[0] for pt in selected_points])/len(selected_points)
    mean_y = sum([pt[1] for pt in selected_points])/len(selected_points)
    mean_z = sum([pt[2] for pt in selected_points])/len(selected_points)
    mean = [mean_x, mean_y, mean_z]
    #ooi_points = np.array([(pt[0], pt[1], pt[2]) for pt in selected_points if [abs(pt_)for pt_ in pt]<=[abs(2*mean_) for mean_ in mean]], dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    ooi_points = np.array([(pt[0], pt[1], pt[2]) for pt in selected_points], dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
    print('OOI',ooi_points)
    print(len(ooi_points), len(selected_points), len(points))
    el = PlyElement.describe(ooi_points, 'vertex')
    PlyData([el]).write(os.path.join(Cropper.INPUT_DIR, '../yollo.ply'))

if __name__ == "__main__":
    read_pointcloud()

import numpy as np
import sys, argparse, copy
from keras.models import load_model
from .readers import mnist_reader
import matplotlib.pyplot as plt

def rms(y_true, y_pred):
    #
    # RMS loss function.
    #
    return np.sqrt(np.mean((y_true - y_pred)**2))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='given some images, labels, and a keras model, raster scan a black block over them and record rms as a heatmap')
    parser.add_argument('--index', default=1, type=int, action='store', help='index of the sample to use')
    parser.add_argument('--imgs', action='store', help='imgs file to use')
    parser.add_argument('--labels', action='store', help='labels file to use'))
    parser.add_argument('--model', action='store', help=' keras model file to use'))
    parser.add_argument('--kernel_size', default=1, type=int, action='store', help='size of black box to use'))

    args = parser.parse_args()

    f_inputs = mnist_reader.open(args.imgs)
    f_labels = mnist_reader.open(args.labels)
    model = load_model(args.model)

    index = args.index
    for i, data in enumerate(f_inputs.samples):
        if i == index:
            s_input = data

    for i, data in enumerate(f_labels.samples):
        if i == index:
            s_label = data

    # What we really care about is how much the error rises relative to using an unperturbed input
    # So establish a baseline prediction
    base_prediction = model.predict(s_input[np.newaxis,:])[0]

    # Assume square images
    img_size = r_input.size()
    kernel_size = args.kernel_size
    # kernel_width is the number of pixels by which the output array is smaller PER SIDE
    # (aka divided by 2) based on the kernel size
    kernel_width = ((kernel_size-1)/2)

    output_array = np.zeros((img_size-(kernel_size-1),img_size-(kernel_size-1)))

    base_img = s_input

    for i,row in enumerate(s_input):
        for j,column_pixel in enumerate(row):
            #check if it is a valid pixel, i.e. we have enough room to construct the block
            if i < img_size-kernel_width and i >= kernel_width and j < img_size-kernel_width and j >= kernel_width:
                x_max = int(i + kernel_width)
                x_min = int(i - kernel_width)
                y_max = int(j + kernel_width)
                y_min = int(j - kernel_width)

                # we don't want our changes to persist, so reset a temporary copy each iteration
                img = copy.deepcopy(base_img)

                for x in range(x_min, x_max+1):
                    for y in range(y_min, y_max+1):
                        img[x, y] = 0


                prediction = model.predict(img[np.newaxis,:])[0] # keras models typically rquire an extra "batch" dimension
                output_array[int(i - kernel_width), int(j - kernel_width)] = rms(base_prediction, prediction)

    extent = 0, img_size, 0, img_size
    base = plt.imshow(base_img, cmap=plt.cm.gray, extent = extent)
    heatmap = plt.imshow(output_array, alpha = 0.5, cmap=plt.cm.inferno, extent = extent)
    plt.colorbar(heatmap)
    plt.show()

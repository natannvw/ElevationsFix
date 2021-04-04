import gpxpy
import numpy
import matplotlib.pyplot as plt
import os
from tkinter.filedialog import askopenfilename


def pars_gpx(filename):
    # function pars_gpx() reading a '.gpx' file, parses it and getting a data of the slopes/gradient
    #
    # input:
    #     filename - '.gpx' file filename
    #
    # output:
    #     gpx            - parsed gpx variable
    #     gradient_list  - list of slopes
    #     elevation_list - list of elevations
    #     std            - STD of slopes
    #     std_factor     - factor of sigmas of STD that you want to differentiate bad slopes

    with open(filename, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        elevation_list = []

        for track in gpx.tracks:
            for segment in track.segments:
                for i in range(len(segment.points)):
                    elevation_list.append(segment.points[i].elevation)

    gradient_list = list(numpy.diff(elevation_list))
    std = numpy.std(gradient_list)
    std_factor = 2.9

    return gpx, gradient_list, elevation_list, std, std_factor


def fix_gradient(gradient_list, std, std_factor):
    # function fix_gradient() fixing the original gradients into a new one list
    #
    # input:
    #     gradient_list  - list of slopes
    #     std            - STD of slopes
    #     std_factor     - factor of sigmas of STD that you want to differentiate bad slopes
    #
    # output:
    #     gradient_list_fixed - list of fixed slopes

    gradient_list_fixed = gradient_list[:]
    for i in range(len(gradient_list)):
        if abs(gradient_list[i]) > (std_factor * std):
            gradient_list_fixed[i] = 0

    return gradient_list_fixed


def update_elevation(gradient_list_fixed, elevation_list):
    # function update_elevation() fixing and updating the original elevations into a new one list
    #
    # input:
    #     gradient_list_fixed - list of fixed slopes
    #     elevation_list      - list of original elevations

    # output:
    #     elevation_list_fixed - list of fixed elevations

    elevation_list_fixed = list(numpy.zeros(len(elevation_list)))
    elevation_list_fixed[0] = elevation_list[0]
    for i in range(len(elevation_list) - 1):
        elevation_list_fixed[i + 1] = elevation_list_fixed[i] + gradient_list_fixed[i]

    return elevation_list_fixed


def update_gpx(gpx, elevation_list_fixed):
    # function update_gpx() updating the original gpx
    #
    # input:
    #     gpx                  - parsed gpx variable
    #     elevation_list_fixed - list of fixed elevations
    #
    # output:
    #     gpx                  - updated parsed gpx variable

    for track in gpx.tracks:
        for segment in track.segments:
            for i in range(len(segment.points)):
                segment.points[i].elevation = elevation_list_fixed[i]

    return gpx


def updated_file(filename, updated_gpx):
    # function updated_file() creates new '.gpx' file from the updated variables
    #
    # input:
    #     filename    - original '.gpx' file filename
    #     updated_gpx - parsed gpx variable

    filename_path = os.path.splitext(filename)
    filename_updated = filename_path[0] + '_updated' + filename_path[1]
    with open(filename_updated, 'w') as gpx_file_updated:
        gpx_file_updated.writelines(updated_gpx.to_xml())


def plots(grad1, elev1, grad2, elev2):
    # function plots() creates plots of of original and updated variables. Used for debugging
    #
    # input:
    #     grad1 - original gradients list
    #     elev1 - original elevations list
    #     grad2 - fixed gradients list
    #     elev2 - fixed elevations list

    # Original plot part:
    points_grad = numpy.linspace(0, len(grad1), len(grad1))
    points_elev = numpy.linspace(0, len(elev1), len(elev1))

    # f, axs = plt.subplots(2,1,figsize=(15,15))

    fig, (ax1, ax2) = plt.subplots(2)
    fig.tight_layout(pad=3.0)

    ax1.plot(points_grad, grad1)
    ax2.plot(points_elev, elev1)
    ax1.set_title('Slope')
    ax2.set_title('Elevation')
    # ax1.legend(gradient_list, elevation_list)
    # ax1.legend(frameon=False, loc='lower center', ncol=2)

    # Updated plot part:
    ax1.plot(points_grad, grad2)
    ax2.plot(points_elev, elev2)

    pos1 = ax2.get_position()  # get the original position
    pos2 = [pos1.x0, pos1.y0 - 0.15, pos1.width, pos1.height]
    ax2.set_position(pos2)  # set a new position

    # fig.legend((l1, ), ('Line 1', 'Line 2'), 'upper left')

    plt.show()


def main():
    # function main() fixes elevation data from a '.gpx' selected file and creates a new updated one same format file

    filename = askopenfilename()                                                   # filename = 'canada-park.gpx'

    gpx, gradient_list, elevation_list, std, std_factor = pars_gpx(filename)
    gradient_list_fixed                                 = fix_gradient(gradient_list, std, std_factor)
    elevation_list_fixed                                = update_elevation(gradient_list_fixed, elevation_list)
    gpx_updated                                         = update_gpx(gpx, elevation_list_fixed)
    updated_file(filename, gpx_updated)
    # plots(gradient_list, elevation_list, gradient_list_fixed, elevation_list_fixed)       # for debugging


main()
#######################################################################################################################
# When finished, to visualize '.gpx' files, use https://www.gpsvisualizer.com/ (or similar website). Then click the
# "three bars" options menu and choose: "Draw an elevation profile" under the "UTILITIES".
#######################################################################################################################

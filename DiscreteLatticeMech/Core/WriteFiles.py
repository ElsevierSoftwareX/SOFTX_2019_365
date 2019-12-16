# -*- coding: utf-8 -*-
"""
Write results into file and make the corresponding plots
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import time


class Writer:

    def __init__(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.folder = './Results_{}'.format(timestr)
        os.mkdir(self.folder)
        print("Results folder: {}".format(self.folder))

    def WriteTensorsToFile(self, InputData, CMatTensor, FlexMatTensor):
        # Store the InputData in the Result file
        with open(self.folder + '/InputData.json', 'w',encoding='utf-8') as outfile:
           json.dump(InputData, outfile, ensure_ascii=False,  indent=6, sort_keys=False)
        # write Cmatrix to file
        np.savetxt(self.folder + '/CMatrix.txt', CMatTensor, fmt='%10.3f')
        # write Flexibility matrix to file
        np.savetxt(self.folder + '/FlexMatrix.txt', FlexMatTensor, fmt='%10.3f')

    def WriteEffectivePropertiesToFile(self, Bulk, Ex, Ey, Poissonyx, Poissonxy, G, rho):
        # write the effective properties to file
        file1 = open(self.folder + "/EffectProperties.txt", "w")
        file1.write("The bulk modulus is K = %10.3f\r\n" % Bulk)
        file1.write("The elastic modulus in the x direction is Ex = %10.3f\r\n" % Ex)
        file1.write("The elastic modulus in the y direction is Ey = %10.3f\r\n" % Ey)
        file1.write("The Poisson's yx value is v_yx = %10.3f\r\n" % Poissonyx)
        file1.write("The Poisson's xy value is v_xy = %10.3f\r\n" % Poissonxy)
        file1.write("The shear modulus is G = %10.3f\r\n" % G)
        file1.write("The relative density is rho = %10.3f\r\n" % rho)
        file1.close()

    def PlotEffectiveProperties(self, Bulk, Ex, Ey, Poissonyx, Poissonxy, G):
        # Plot the normal, shear and bulk moduli to file
        plt.figure(1)
        names = ['Ex', 'Ey', 'K', 'G']
        values = [Ex, Ey, Bulk, G]
        barlist = plt.bar(names, values)
        plt.suptitle('Normal, Shear and Bulk Moduli')
        barlist[0].set_color('b')
        barlist[1].set_color('b')
        barlist[2].set_color('r')
        barlist[3].set_color('g')
        plt.xticks(rotation='82.5')
        plt.savefig(self.folder + '/NSB_Moduli.png', dpi=400)

        # plot the poisson's ratio values
        plt.figure(2)
        names = [r'$\nu_{yx}$', r'$\nu_{xy}$']
        values = [Poissonyx, Poissonxy]
        barplot=plt.bar(names, values)
        barplot[0].set_color('g')
        barplot[1].set_color('b')
        plt.suptitle('Poisson ratio values per direction')
        plt.xticks(rotation='82.5')
        plt.savefig(self.folder + '/PoissonRation.png', dpi=400)

        # plot the normal to shear ratio for each direction
        plt.figure(3)
        names = ['Ex/G', 'Ey/G']
        values = [Ex/G, Ey/G]
        barplot1 = plt.bar(names, values)
        barplot1[0].set_color('g')
        barplot1[1].set_color('b')
        plt.suptitle('Normal to shear ratio per direction')
        plt.xticks(rotation='82.5')
        plt.savefig(self.folder + '/NormalToShear.png', dpi=400)

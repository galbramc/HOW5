from Joukowski import make_joukowski

# Q is the degree of the polynomial used to represent elements. For Finite Volume/Difference codes, this should be Q=1 for linear elements.
# Finite Element codes are encouraged to use super-parametric elements with Q=4, or the highest available
Q = 4

#The range of refinement levels to generate
refmin = 0
refmax = 5

#Set to True for triangle grids, and False for qauds
TriFlag=False

#Used to specify the file format to dump. See Joukowski.make_joukowski for details
FileFormat="gmsh"

#Grid distrubution, "Classic" or "Challenge"
Distribution = "Classic"

for ref in xrange(refmin,refmax+1):
    make_joukowski(ref, Q, TriFlag, Distribution, FileFormat, reynolds=1000,
                   filename_base="Joukowski_Laminar_" + Distribution )

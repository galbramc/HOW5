import numpy as npy
from plot3d import writeOVERFLOW, writePlot2D, writePlot3D, writePlot3Dxz
from gmsh import writeGMSH_Quad, writeGMSH_Tri

#===============================================================================
def writeGMSH(filename_base, ref, Q, TriFlag, E, V, NC, ni, nj):

    filename = filename_base + ('_tri' if TriFlag else '_quad') + '_ref'+str(ref)+ '_Q'+str(Q)+'.msh'
    print 'Writing ', filename
    f = open(filename, 'w')

    fac = 2 if TriFlag else 1

    nelem = E.shape[0];
    nnode = V.shape[0];
    
    nInflow = int((nj-1)/Q)
    nOutflow = nInflow
    nWall = int((ni-1)/Q)

    floatformat = "{:3.16e}"
    
    #Write out the Gmsh file format
    f.write('$MeshFormat\n')
    f.write('2.2 0 8\n')
    f.write('$EndMeshFormat\n')
    f.write('$Nodes\n')
    f.write(str(nnode)+'\n')
    for i in xrange(nnode):
        f.write("{:2d}".format(i+1) + ' ' + floatformat.format(V[i,0]) + ' ' + floatformat.format(V[i,1]) + ' 0.0\n')
    f.write('$EndNodes\n')

    f.write('$Elements\n')
    f.write(str(4 + fac*nelem+nInflow+nOutflow+2*nWall)+'\n')

    #----------------#
    # Corners        #
    #----------------#

    f.write('1 15 2 0 6 ' + str(NC[ 0, 0]) + '\n')
    f.write('2 15 2 0 6 ' + str(NC[-1, 0]) + '\n')
    f.write('3 15 2 0 6 ' + str(NC[-1,-1]) + '\n')
    f.write('4 15 2 0 6 ' + str(NC[ 0,-1]) + '\n')

    if Q == 1: GmshLineType = 1 #2-node line
    if Q == 2: GmshLineType = 8 #3-node line
    if Q == 3: GmshLineType = 26 #4-node line
    if Q == 4: GmshLineType = 27 #5-node line
    
    #----------------#
    # Boundary faces #
    #----------------#

    # Inflow
    BC = 1
    for j in xrange(nInflow):
        f.write(str(j+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[0,Q*j]) + ' ' + str(NC[0,Q*(j+1)]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[0,Q*j+q]) + ' ')
        f.write('\n')
      
    # Outflow
    BC = 2
    for j in xrange(nOutflow):
        f.write(str(nInflow+j+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[ni-1,Q*j]) + ' ' + str(NC[ni-1,Q*(j+1)]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[ni-1,Q*j+q]) + ' ')
        f.write('\n')

    # Walls
    BC = 3
    for i in xrange(nWall):
        f.write(str(nInflow+nOutflow+i+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[Q*i,0]) + ' ' + str(NC[Q*(i+1),0]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[Q*i+q,0]) + ' ')
        f.write('\n')
        
    BC = 4
    for i in xrange(nWall):
        f.write(str(nInflow+nOutflow+nWall+i+5) + ' ' + str(GmshLineType) + ' 2 0 ' + str(BC) + ' ')
        #Write end points
        f.write(str(NC[Q*i,nj-1]) + ' ' + str(NC[Q*(i+1),nj-1]) + ' ')
        #Write higher-order nodes
        for q in xrange(1,Q):
            f.write(str(NC[Q*i+q,nj-1]) + ' ')
        f.write('\n')

    nBCelem = 2*nWall+nInflow+nOutflow

    if TriFlag:
        writeGMSH_Tri(f, nelem, nBCelem, Q, E, NC)
    else:
        writeGMSH_Quad(f, nelem, nBCelem, Q, E)

    f.write('$EndElements\n')
    f.write('$PhysicalNames\n')
    f.write('5\n')
    f.write('2 0 \"MeshInterior\"\n')
    f.write('1 1 \"Inflow\"\n')
    f.write('1 2 \"Outflow\"\n')
    f.write('1 3 \"Lower Wall\"\n')
    f.write('1 4 \"Upper Wall\"\n')
    f.write('$EndPhysicalNames\n')
    
    
    f.close()

#-----------------------------------
def block_elem(N, Q):
    nx, ny = N.shape;
    #if (Q != 1) and ((mod(nx,Q) != 1) or (mod(ny,Q) != 1)): print('ERROR 2'); return;
    mx = int((nx-1)/Q);
    my = int((ny-1)/Q);
    E = npy.zeros( (mx*my,(Q+1)*(Q+1)),int);
    dy = ny;
    i = 0;
    for imy in xrange(my):
      for imx in xrange(mx):
        ix = Q*(imx+1)-(Q-1)-1;
        iy = Q*(imy+1)-(Q-1)-1;
        k = 0;
        for ky in xrange(Q+1):
          for kx in xrange(Q+1):
            E[i,k] = N[ix+kx,iy+ky]
            k = k+1;

        i = i + 1;
      
    return E

#-----------------------------------------------------------
# writes BC information for FUN3D
def writeNMF(fname, ni, nj):

    nk = 2
    # NMF file expects all comments and extra empty lines
    f = open(fname, 'w')
    f.write('# ===== Neutral Map File generated by Python  =====\n')
    f.write('# ===================================================================================\n')
    f.write('# Block# IDIM JDIM KDIM\n')
    f.write('# -----------------------------------------------------------------------------------\n')
    f.write('1\n\n')
    f.write(str(ni) + ' ' + str(nj) + ' ' + str(nk) + '\n\n')
    f.write('# ===================================================================================\n')
    f.write('# Type            B1 F1   S1 E1   S2 E2   B2 F2   S1 E1   S2 E2   Swap\n')
    f.write('# -----------------------------------------------------------------------------------\n')
    f.write("'tangency'        1 1   1 " + str(ni) + "   1 " +str(nj) + "\n")
    f.write("'tangency'        1 2   1 " + str(ni) + "   1 " +str(nj) + "\n")
    f.write("'Subsonic inflow' 1 3   1 " + str(nj) + "   1 " +str(nk) + "\n")
    f.write("'Back pressure'   1 4   1 " + str(nj) + "   1 " +str(nk) + "\n")
    f.write("'tangency'        1 5   1 " + str(nk) + "   1 " +str(ni) + "\n")
    f.write("'tangency'        1 6   1 " + str(nk) + "   1 " +str(ni) + "\n")


#===============================================================================
def writeGRM(filename_base, ref, Q, TriFlag, E, V, NC, ni, nj):
    #=========================#
    # Write out the grid file #
    #=========================#

    filename = filename_base + ('_tri' if TriFlag else '_quad') + '_ref'+str(ref)+ '_Q'+str(Q)+'.grm'
    print 'Writing ', filename
    f = open(filename, 'w')
     
    nelem = E.shape[0];
    nnode = V.shape[0];
    
    nInflow = int((nj-1)/Q)
    nOutflow = nInflow
    nWall = int((ni-1)/Q)
    
    fac = 2 if TriFlag else 1
    
    f.write('2 ' + str(nnode) + ' 1 4\n') #dim nNodes negrp nbfgrp
     
    #----------#
    # Vertices #
    #----------#
    floatformat = "{:3.16e}"
    
    for i in xrange(nnode):
        f.write(floatformat.format(V[i,0]) + ' ' + floatformat.format(V[i,1]) + '\n')
      
    #----------------#
    # Boundary faces #
    #----------------#
        
    # Inflow
    f.write(str(nInflow) + '\n');
    f.write('PXE_Shape_Edge\n')
    for j in xrange(nInflow):
        f.write(str(NC[0,Q*j]) + ' ' + str(NC[0,Q*(j+1)]) + '\n')
    
    # Outflow
    f.write(str(nOutflow) + '\n')
    f.write('PXE_Shape_Edge\n')
    for j in xrange(nOutflow):
        f.write(str(NC[ni-1,Q*j]) + ' ' + str(NC[ni-1,Q*(j+1)]) + '\n')
      
    # Walls
    f.write(str(nWall) + '\n')
    f.write('PXE_Shape_Edge\n')
    for i in xrange(nWall):
        f.write(str(NC[Q*i,0]) + ' ' + str(NC[Q*(i+1),0]) + '\n')

    f.write(str(nWall) + '\n')
    f.write('PXE_Shape_Edge\n')
    for i in xrange(nWall):
        f.write(str(NC[Q*i,nj-1]) + ' ' + str(NC[Q*(i+1),nj-1]) + '\n')
    
    #----------#
    # Elements #
    #----------#
      
    if TriFlag:
        f.write(str(2*nelem)+'\n')
        f.write(str(Q)+'\n')
        f.write('PXE_Shape_Triangle\n')
        f.write('UniformNodeDistribution\n')

        ni = int((NC.shape[0]-1)/Q)
        nj = int((NC.shape[1]-1)/Q)
        
        if Q == 1:
            nodemap = (0,  1, 
                       2, -1)
            nodemap2= (0, 1, 
                      -1, 2)
        if Q == 2:
            nodemap = (0,  5,  1, 
                       4,  3, -1,   
                       2, -1, -1)
            
            nodemap2= ( 0,  5,  1, 
                       -1,  4,  3,   
                       -1, -1,  2)
    
        if Q == 3:
            nodemap = ( 0,  7,  8,  1, 
                        6,  9,  3, -1, 
                        5,  4, -1, -1, 
                        2, -1, -1, -1)
            nodemap2= ( 0,  7,  8,  1, 
                       -1,  6,  9,  3, 
                       -1, -1,  5,  4, 
                       -1, -1, -1,  2)
        if Q == 4:
            nodemap = ( 0,  9, 10, 11,  1, 
                        8, 12, 13,  3, -1, 
                        7, 14,  4, -1, -1, 
                        6,  5, -1, -1, -1, 
                        2, -1, -1, -1, -1, )
            nodemap2= ( 0,  9, 10, 11,  1, 
                       -1,  8, 12, 13,  3, 
                       -1, -1,  7, 14,  4,
                       -1, -1, -1,  6,  5, 
                       -1, -1, -1, -1,  2,)
        
        #Invert the map
        nodemapinv  = []
        for k in xrange(int((Q+1)*(Q+2)/2)):
            j = 0
            while nodemap[j] != k: j += 1
            nodemapinv.append(j)
    
        nodemapinv2  = []
        for k in xrange(int((Q+1)*(Q+2)/2)):
            j = 0
            while nodemap2[j] != k: j += 1
            nodemapinv2.append(j)

        for j in xrange(nj):
            for i in xrange(int(ni/2)):
                e = i + ni*j
                
                #Write nodes
                for k in xrange(int((Q+1)*(Q+2)/2)):
                    f.write(str(E[e,nodemapinv[k]])+' ')
                f.write('\n')
        
                
                #Write nodes
                for k in xrange(int((Q+1)*(Q+2)/2)):
                    f.write(str(E[e,(Q+1)*(Q+1)-1-nodemapinv[k]])+' ')
                f.write('\n')
                
            for i in xrange(int(ni/2),ni):
                e = i + ni*j
                
                #Write nodes
                for k in xrange(int((Q+1)*(Q+2)/2)):
                    f.write(str(E[e,nodemapinv2[k]])+' ')
                f.write('\n')
                        
                #Write nodes
                for k in xrange(int((Q+1)*(Q+2)/2)):
                    f.write(str(E[e,(Q+1)*(Q+1)-1-nodemapinv2[k]])+' ')
                f.write('\n')

    else:
        f.write(str(nelem)+'\n')
        f.write(str(Q)+'\n')
        f.write('PXE_Shape_Quad\n')
        f.write('UniformNodeDistribution\n')
        #Write nodes
        for e in xrange(nelem):
            for k in xrange((Q+1)*(Q+1)):
                f.write(str(E[e,k])+' ')
            f.write('\n')
      
    f.close()
    return

#===============================================================================
def SmoothBump(ni, nj, Q, ref, TriFlag, FileFormat):

    fac = 2 if TriFlag else 1
    
    ni = ni*Q*2**ref+1
    nj = nj*Q*2**ref+1

    print 'Cell size ' + str( int((ni-1)/Q) ) + 'x' + str( int((nj-1)/2) ) + ' with '  + str( fac*int((ni-1)/Q)*int((nj-1)/2) ) + ' Elements'
    
    #Create all the vertexes
    V = npy.zeros((ni,nj,2),float)

    #Upper boundary
    y1 = 0.8
    x0 = npy.linspace(-1.5, 1.5, ni)

    for i in xrange(ni):
        x = x0[i];
        y0 = 0.0625*npy.exp(-25.*x**2)
        y = npy.linspace(y0, y1, nj)
        V[i,:,0] = x
        V[i,:,1] = y


    if FileFormat == 'p2d':
        writePlot2D('SmoothBump_ref'+str(ref)+ '_Q'+str(Q)+'.p2d.x', V[:,:,0], V[:,:,1])
    if FileFormat == 'p3dxy':
        writeNMF('SmoothBump_ref'+str(ref)+'.nmf', ni, nj)
        writePlot3D('SmoothBump_ref'+str(ref)+ '_Q'+str(Q)+'.p3d', V[:,:,0], V[:,:,1])
    if FileFormat == 'p3dxz':
        writeNMF('SmoothBump_ref'+str(ref)+'.nmf', ni, nj)
        writePlot3Dxz('SmoothBump_ref'+str(ref)+'.p3d', V[:,:,0], V[:,:,1])
    if FileFormat == 'in':
        writeOVERFLOW('grid.in.'+str(ref), V[:,:,0], V[:,:,1])

    
    V = V.reshape( (ni*nj,2) )
    
    #---------------------------------------------#
    # node number matrices for writing out blocks #
    #---------------------------------------------#

    NC = npy.arange(ni*nj).reshape( (ni, nj) )+1
    
    #---------------#
    # form elements #
    #---------------#
    E = block_elem(NC, Q);

    if FileFormat == 'msh':
        writeGMSH('SmoothBump', ref, Q, TriFlag, E, V, NC, ni, nj)
    if FileFormat == 'grm':
        writeGRM('SmoothBump', ref, Q, TriFlag, E, V, NC, ni, nj)


# Q is the degree of the polynomial used to represent elements. For Finite Volume/Difference codes, this should be Q=1 for linear elements.
# Finite Element codes are encouraged to use super-parametric elements with Q=4, or the highest available
Q = 4

#The range of refinement levels to generate
refmin = 0
refmax = 5

#Set to True for triangle grids, and False for qauds
TriFlag=True

for ref in xrange(refmin,refmax+1):
    SmoothBump(ni=6, nj=2, Q=Q, ref=ref, TriFlag=TriFlag, FileFormat="msh")

    

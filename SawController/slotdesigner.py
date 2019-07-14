#!/usr/bin/env python

## Produce text describing c-arrays for saw positions required by box cut
## joints
##
## Rules saw position is relative to the left side of the blade.
## 0 has the blade touching the board edge.
## The pattern specified here must not have a cut at the right board edge.
## The automatically inverted version will have the corresponding cut
##
##
##     |                                 |
##     |                                 |
##     |                                 |
##     |    ____    ____      ______     |
##     |____|  |____|  |______|    |_____|
##     G    F  E    D  C      B    A      0
##
##
##    patright = [A C E G]
##    patleft = [0 B D F]
##
## Adjust patright by kerfwidth
##   patright += kerfwidth
## to produce positions relative to the lhs of blade
##
##    patinvright = patleft
## Adjust
##    patinvright += kerfwidth
##    patinvleft = patright
##
## Possibly adjust one or both with a tolerance, which corresponds to
## reducing the kerfwidth slightly
##
##
## Design options
##
## 1) Designated width slot, specified board width
##
## 2) Designated number of slots, given board width
##
## 3) Other functions with varying widths

import numpy as np

## Thread is one turn for 5mm, 200 steps per turn. TODO - check accuracy of 
## this scale. Multiply position in mm by this to get position in steps
stepscale=200/5

def mkPatInv(pat):
    return({'leftpat': pat['rightpat'], 'rightpat': pat['leftpat']})

def adjustRight(pat, kerfwidth):
    res={'rightpat':pat['rightpat'].copy(), 'leftpat':pat['leftpat'].copy()}

    res['rightpat'] += kerfwidth
    return(res)

def mkSlotsA(slotwidth, boardwidth):
    ## if the total is an odd number, then the first pattern
    ## will have a pin on each side
    total=round(boardwidth/slotwidth)

    left = np.arange(start=0, stop=boardwidth, step=2*slotwidth)
    right = np.arange(start=slotwidth, stop=boardwidth, step=2*slotwidth)

    return({'leftpat': left, 'rightpat': right})

def mkSlotsB(count, boardwidth):
    # count is the number of pins in the first pattern
    # always have a pin at either end
    totalEdges=2*count
    alledges = np.linspace(0, boardwidth, num=totalEdges)
    leftidx=np.arange(start=0, stop=len(alledges), step=2)
    rightidx=np.arange(start=1, stop=len(alledges), step=2)
    res={'leftpat': alledges[leftidx], 'rightpat':alledges[rightidx]}
    return(res)


def dumpPattern(pat, filename, kerfwidth):
    invpat = mkPatInv(pat)
    # prune the pin pattern
    pat['leftpat']=pat['leftpat'][1:]
    pat['rightpat']=pat['rightpat'][:-1]
    print("Slot width = ", pat['leftpat'][0] - pat['rightpat'][0])
    #print(pat)
    #print(invpat)
    invpat=adjustRight(invpat, kerfwidth)
    pat=adjustRight(pat, kerfwidth)

    rightposlen=len(pat['rightpat'])
    leftposlen = len(pat['leftpat'])

    # combine left and right into one array
    #
    cutpos=np.concatenate((pat['rightpat'], pat['leftpat']))
    cutpos.sort()
    print(cutpos)
    cutpos = np.round(stepscale*cutpos)
    cutpos = cutpos.astype(int)
    f = open(filename, 'w')
    f.write("#ifndef _slots_h\n")
    f.write("#define _slots_h\n")


    def writeArray(arr, name, lenname):
        arrlen=len(arr)
        f.write("const int " + lenname + " = " + str(arrlen) + ";\n")
        f.write("const uint32_t " + name + "[" + lenname + "]={")
        for i in range(arrlen):
            if i != 0:
                f.write(", ")
            f.write(str(arr[i]))
        f.write("};\n")

    #writeArray(pat['leftpat'], 'leftpos', 'leftposlen')
    #writeArray(pat['rightpat'], 'rightpos', 'rightposlen')

    #writeArray(invpat['leftpat'], 'invleftpos', 'invleftposlen')
    #writeArray(invpat['rightpat'], 'invrightpos', 'invrightposlen')
    #f.write("const float *currentRightCuts;\n")
    #f.write("const float *currentLeftCuts;\n")
    #f.write("int currentRightLen;\n")
    #f.write("int currentLeftLen;\n")
    writeArray(cutpos, "cutsteparray", "TotalCuts")
    f.write("#endif\n")
    f.close()
    ## write out the declarations
    # f = open(filenamedec, 'w')
    # f.write("#ifndef _slotsdec_h\n")
    # f.write("#define _slotsdec_h\n")
    # f.write("extern const float kerfwidth;\n")
    # f.write("extern const int leftposlen, rightposlen, invleftposlen, invrightposlen;\n")
    # f.write("extern int currentLeftLen, currentRightLen;\n")
    # f.write("extern const float leftpos[], rightpos[], invleftpos[], invrightpos[];\n")
    # f.write("extern const float *currentRightCuts;\n")
    # f.write("extern const float *currentLeftCuts;\n")
    # f.write("#endif\n")
    # f.close()
############################################
## code to generate the patterns here
## test version : 5 pins, 100mm board

p1=mkSlotsB(5, 100)

# Estimate kerf for the "allpurpose blade"
dumpPattern(p1, "targetsteps.h", 2.7)


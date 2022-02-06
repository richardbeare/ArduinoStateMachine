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

## Thread is one turn for 5mm, 400 steps per turn. TODO - check accuracy of 
## this scale. Multiply position in mm by this to get position in steps
stepscale=400/5

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


def dumpPattern(pat, filename, kerfwidth, extracuts=False):
    invpat = mkPatInv(pat)
    # prune the pin pattern

    pat['leftpat']=pat['leftpat'][1:]
    pat['rightpat']=pat['rightpat'][:-1]
    #invpat['leftpat'] = invpat['leftpat'][:-1]
    #invpat['rightpat'] = invpat['rightpat'][1:]
    print("Slot width = ", pat['leftpat'][0] - pat['rightpat'][0])

    invpat=adjustRight(invpat, kerfwidth)
    pat=adjustRight(pat, kerfwidth)

    print("pat=", pat)
    print("invpat=", invpat)

    rightposlen=len(pat['rightpat'])
    leftposlen = len(pat['leftpat'])

    # combine left and right into one array
    #
    if extracuts:
        # include cuts to isolate the pins
        def InsertCuts(right, left):
            result=list()
            k=len(right)
            for i in range(k):
                first=right[i]
                last=left[i]
                newcuts=np.linspace(first, last, num=2+np.round((last-first)/(kerfwidth)))
                result.append(newcuts)
            #result.sort()
            result=np.concatenate(result)
            result.sort()
            return(result)
        cutpos=InsertCuts(pat['rightpat'], pat['leftpat'])
        cutpos2=InsertCuts(invpat['rightpat'], invpat['leftpat'])

    else:
        cutpos=np.concatenate((pat['rightpat'], pat['leftpat']))
        cutpos.sort()
        cutpos2=np.concatenate((invpat['rightpat'], invpat['leftpat']))
        cutpos2.sort()

    print(cutpos)
    cutpos = np.round(stepscale*cutpos)
    cutpos = cutpos.astype(int)

    print(cutpos)
    cutpos2 = np.round(stepscale*cutpos2)
    cutpos2 = cutpos2.astype(int)
    print(cutpos2)

    f = open(filename, 'w')
    f.write("#ifndef _slots_h\n")
    f.write("#define _slots_h\n")


    def writeArray(arr, name, lenname):
        arrlen=len(arr)
        f.write("const uint16_t " + lenname + " = " + str(arrlen) + ";\n")
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
    writeArray(cutpos, "cutsteparray1", "TotalCuts1")

    
    writeArray(cutpos2, "cutsteparray2", "TotalCuts2")
    f.write("const uint32_t* cutsteparray = cutsteparray1;\n")
    f.write("uint16_t TotalCuts = TotalCuts1;\n")

    f.write("#endif\n")
    f.close()



############################################
## code to generate the patterns here
## test version : 5 pins, 100mm board

#p1=mkSlotsB(4, 82.55)

# vertical edges of test box. Ply is 9mm
#p1 = mkSlotsB(7, 129)

# base of box - short edge
#p1 = mkSlotsB(4, 107.5)
#p1 = mkSlotsB(7, 237.5)
#p1 = mkSlotsB(4, 62)

#p1 = mkSlotsB(5, 100)
p1 = mkSlotsB(15, 300)

# Estimate kerf for the "allpurpose blade"
#dumpPattern(p1, "targetsteps.h", 2.675, extracuts=True)

# Kerf for wood blades is 2.5mm. Measure a piece, cut in two, measure
# the two pieces and take the difference
# result was 2.5mm
# Also says this on the blade.
dumpPattern(p1, "targetsteps.h", 2.5, extracuts=True)

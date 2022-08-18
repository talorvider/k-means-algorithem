import matplotlib.pyplot as plt
import numpy as np
import sys
import os

image_fname, centroids_fname, out_fname = sys.argv[1], sys.argv[2], sys.argv[3]


#create a list from first cantroids
def perparedFirstCentroids():
    firstCentroids =[]
    with open(centroids_fname) as file:
        lines = file.readlines()
        for line in lines:
            centroid = []
            line = line.rstrip()
            for word in line.split():
                centroid.append(float(word))
            firstCentroids.append(centroid)
        return firstCentroids

#calculate the closest centroid to pixel and return the centroid index
def findClosestCentroid(centroids, pixel):
    pixelDist = float('inf')
    centroidIndex = 0
    for index, centroid in enumerate(centroids):
        distance = np.sqrt((centroid[0]-pixel[0])**2 + (centroid[1]-pixel[1])**2 + (centroid[2]-pixel[2])**2)
        # save the index of closest centroid
        if pixelDist > distance:
            pixelDist = distance
            centroidIndex = index
    return centroidIndex

#calculate the new position of centroids 
def calcNewCentrodsPosition(centroids, pixels, cluster):
    newCentroidsPos = []
    #find all pixels for each centroid
    for centIndx, centroid in enumerate(centroids):
        pixelsIndexs = np.where(cluster == centIndx)[0]
        pixelsPerCentroid = [pixels[i] for i in pixelsIndexs]
        #chek if there is no pixel for this centroid - save the last position of centroid
        if (len(pixelsPerCentroid) == 0):
            newCentroidsPos.append(centroid)
        else:
            pixelsSum = np.sum(pixelsPerCentroid, axis=0)
            centroidPos = np.divide(pixelsSum, len(pixelsPerCentroid))
            newCentroidsPos.append(centroidPos.round(4))
    return newCentroidsPos

#write all the iteration into file
def writeToFile(allMoves):
    outFile = os.open(out_fname, os.O_RDWR | os.O_CREAT)
    for i, move in enumerate(allMoves):
        line = f"[iter {i}]:{','.join([str(i) for i in move])}\n"
        l = str.encode(line)
        numBytes = os.write(outFile, l)
    os.close(outFile)

#check how many digit there is after point
def returnLenAfterPoint(pixel):
    #for r, g, b
    catLenIndex = []
    for i, color in enumerate(pixel):
        s = str(color)
        if not '.' in s:
            catLenIndex[i] = 0
            continue
        if( len(s) - s.index('.') - 1 > 4):
            catLenIndex[i] = 1
        
#update pixels data by centroid
def updatePixels(centroids, pixels, cluster):
    for centIndx, centroid in enumerate(centroids):
        pixelsIndexs = np.where(cluster == centIndx)[0]
        #pixelsPerCentroid = [pixels[i] for i in pixelsIndexs]
        for i, pixelIndx in enumerate(pixelsIndexs):
            pixels[pixelIndx] = centroid
    return pixels


def kmeansAlgo():
    z = np.loadtxt(centroids_fname)  # load centroids
    orig_pixels = plt.imread(image_fname)
    pixels = orig_pixels.astype(float) / 255.
    # Reshape the image(128x128x3) into an Nx3 matrix where N = number of pixels.
    pixels = pixels.reshape(-1, 3)
    centroids = perparedFirstCentroids()
    centroids = np.array(centroids)
    newCentroids = []
    allMoves = []
    #create list with 0 for cluster
    cluster = np.zeros(pixels.shape[0])
    #run 20 iteration of algo
    for j in range(20):
        for i, pixel in enumerate(pixels):
            closestCentroidIndx = findClosestCentroid(centroids, pixel)
            #update the cluster that this pixel is closest to that centroid
            cluster[i] = closestCentroidIndx
        newCentroids = calcNewCentrodsPosition(centroids, pixels, cluster)
        allMoves.append(newCentroids)
        # if the centroids is not change stup the algo 
        if np.array_equal(centroids, newCentroids):
            writeToFile(allMoves)
            pixels = updatePixels(centroids, pixels, cluster)
            return
        else:
            centroids = newCentroids
    writeToFile(allMoves)
    pixels= updatePixels(centroids, pixels, cluster)
    
     
kmeansAlgo()

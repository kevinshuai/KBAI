# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
# Not sure if I need ImageDraw, but I will put it there for now
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps, ImageStat, ImageMath
import numpy

class Agent:

    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self,problem):

        # Save the problem in a member variable so the class can use it
        self.rpm = problem

        # Initialize the best guesses
        best_answer = -1
        best_confidence_rating = 0.0       

        # Solve 2x2 matrices
        if problem.problemType == "2x2":
            self.Open2x2Figures()

            best_answer, best_confidence_rating = self.Solve2x2RPM()
        # Solve 3x3 matrices
        elif problem.problemType == "3x3":
            self.Open3x3Figures()

            best_answer, best_confidence_rating = self.Solve3x3RPM()
        #end if

        return best_answer
    #end def

    # This method will run through a number of image transformations and attempt to
    # find the best solution to a 2x2 RPM
    # Find the best transformation between A and B and between A and C. Then apply those
    # transformations to from C to D and from B to D 
    def Solve2x2RPM(self):
        best_answer = -1
        best_confidence = 0.0
        best_AB_transformation = "NoTransform"
        best_AC_transformation = "NoTransform"

        # Find A to B transformation
        best_AB_transformation = self.FindA2BTransform()

        # Find A to C transformation
        best_AC_transformation = self.FindA2CTransform()

        # Apply given transforms
        #temp_best_answer = self.ApplyBestTransforms(best_AB_transformation, best_AC_transformation)  







        # No transformation - just take A and compare to B

        # Rotation

        # Reflection

        # By difference I mean absolute value difference
        # Find difference between A and B and between A and C
        # The difference between A and B subtract from C (x)
        # The difference between A and C subtract from B (y)
        # Combine the two differences (x and y)

        # I am wondering if I need an operator to tell me what is in B that is not in A (what is new in B)
        # Some things are just simple addition and subtraction. In some cases between A and B some things are
        # removed, but some things are added. 
        # Would just B - A work and not take the absolute value? This would start with B and remove everything that
        # is in A.
    
        return -1, 0.0
    #end def

    # Finds the best transform between A and B for a 2x2 matrix
    def FindA2BTransform(self):
        best_transform = "NoTransformation"
        least_diff = 1.0
        best_confidence = 0.0

        # No transform
        # Compare A to B directly
        diff = self.Compare2Images(self.A, self.B);
        if diff < least_diff:
            least_diff = diff
            best_transform = "NoTransformation"
        

        # Rotation

        # Reflection

        # AND

        # OR

        confidence = 1.0-least_diff

        return best_transform, confidence
    #end def

    # Finds the best transformation between A and C for a 2x2 matrix
    def FindA2CTransform(self):
        best_transform = "NoTransformation"

        # No transform
        

        # Rotation

        # Reflection

        # AND

        # OR

        return best_transform
    #end def

    # This method will run through a number of image transformations and attempt to
    # find the best solution to for a 2x2 RPM
    def Solve3x3RPM(self):

        return -1, 0.0
    #end def


    # This method takes in an image that represents a potential answer
    # Returns a value between 0 and 1 that represent the similarity
    def CompareGuessToAnswers(self, guess):
        diff = 1.0 
        best_match = -1

        if(self.rpm.problemType == "2x2"):
            for i in range(1,7):
                # Find the percent difference between guess and answer
                self.Compare2Images(guess, self.answers[str(i)])
                
                if temp_diff < diff:
                    best_match = i
                    diff = temp_diff
                
            #end for
        #end if
        elif(mat_size == "3x3"):
            for i in range(1,9):
                img_diff = ImageChops.difference(self.answers[str(i)], guess)
            #end for
        #end if

        return best_match, diff
    #end def

    # Compares two images, returns a percentage of pixels different
    def Compare2Images(self, imgA, imgB):
        # Find the absolute difference between the two images
        img_diff = ImageChops.difference(imgA, imgB)

        # Get the size of the difference image
        img_diff_size = img_diff.size[0] * img_diff.size[1]   

        #img_diff.show()

        # TODO Do some cleanup to the image here
        # Some of the images don't perfectly line up so when the difference is taken there 
        # are some artifacts
        

        # TODO Find the total number of pixels that are different (black)
        num_pixels_diff = 0

        # Calculate the percentage
        diff_percentage = float(num_pixels_diff)/img_diff_size  

        return diff_percentage
    #end def


    # Opens and saves all the figures for a 2x2 RPM
    def Open2x2Figures(self):
        # Initialize all the images
        self.A = Image.open(self.rpm.figures["A"].visualFilename)
        self.B = Image.open(self.rpm.figures["B"].visualFilename)
        self.C = Image.open(self.rpm.figures["C"].visualFilename)
        self.A1 = Image.open(self.rpm.figures["1"].visualFilename)
        self.A2 = Image.open(self.rpm.figures["2"].visualFilename)
        self.A3 = Image.open(self.rpm.figures["3"].visualFilename)
        self.A4 = Image.open(self.rpm.figures["4"].visualFilename)
        self.A5 = Image.open(self.rpm.figures["5"].visualFilename)
        self.A6 = Image.open(self.rpm.figures["6"].visualFilename)

        self.answers = {"1": self.A1,
                        "2": self.A2,
                        "3": self.A3,
                        "4": self.A4,
                        "5": self.A5,
                        "6": self.A6 }
    #end def

    def Open3x3Figures(self):
        # Initialize all the images
        self.A = Image.open(self.rpm.figures["A"].visualFilename)
        self.B = Image.open(self.rpm.figures["B"].visualFilename)
        self.C = Image.open(self.rpm.figures["C"].visualFilename)
        self.A1 = Image.open(self.rpm.figures["1"].visualFilename)
        self.A2 = Image.open(self.rpm.figures["2"].visualFilename)
        self.A3 = Image.open(self.rpm.figures["3"].visualFilename)
        self.A4 = Image.open(self.rpm.figures["4"].visualFilename)
        self.A5 = Image.open(self.rpm.figures["5"].visualFilename)
        self.A6 = Image.open(self.rpm.figures["6"].visualFilename)
    #end def



#end class
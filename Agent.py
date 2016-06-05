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
            print self.rpm.name

            best_answer, best_confidence_rating = self.Solve2x2RPM()

            print " Answer: ", best_answer, " Confidence: ", best_confidence_rating
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
        confidence = 0.0
        best_AB_transformation = "NoMatch"
        best_AC_transformation = "NoMatch"

        # Find A to B transformation
        best_AB_transformation, AB_confidence = self.FindA2BTransform()

        print best_AB_transformation

        # Find A to C transformation
        print "  Finding best AC transform..."
        best_AC_transformation, AC_confidence = self.FindA2CTransform()

        # Apply given transforms and compare to answers, returning best one
        simple_answer, simple_confidence = self.ApplyBestTransforms(best_AB_transformation, best_AC_transformation)  

        # The above methods allow for simple transformations between A and B and A and C
        # This essentially treats them as separate 2x1 problems which are then combined later
        # This works for many problems but not all. Sometimes a more complicated transformation is
        # required. These will be handled here
        complex_answer, complex_confidence = self.HandleNoMatch(best_AB_transformation, best_AC_transformation)

        if complex_confidence > simple_confidence:
            best_answer = complex_answer
            confidence = complex_confidence
        else:
            best_answer = simple_answer
            confidence = simple_confidence
    
        # TODO: What about multiple correct answers?
        # Resolve using confidence values?

        return best_answer, confidence
    #end def

    # Finds the best transform between A and B for a 2x2 matrix
    def FindA2BTransform(self):
        best_transform, confidence = self.FindBestSimpleTransformation(self.A, self.B)

        return best_transform, confidence
    #end def

    # Finds the best transformation between A and C for a 2x2 matrix
    def FindA2CTransform(self):
        best_transform, confidence = self.FindBestSimpleTransformation(self.A, self.C)

        return best_transform, confidence
    #end def

    # Only handles simple geometric transforms
    def FindBestSimpleTransformation(self, imgA, imgB):
        best_transform = "NoMatch"
        least_diff = 1.0
        imgA_xform = imgA

        # No transform
        diff = self.Compare2Images(imgA_xform, imgB)
        if diff < least_diff:
            least_diff = diff
            best_transform = "NoTransformation"

        # Rotation
        # 90 CCW
        imgA_xform = imgA.rotate(90)
        diff = self.Compare2Images(imgA_xform, imgB)
        if "B-06" in self.rpm.name:
            print "    Rotation CCW: ", diff
            imgA_xform.show()
        if diff < least_diff:
            least_diff = diff
            best_transform = "Rotation90CW"

        # 90 CW
        imgA_xform = imgA.rotate(270)
        diff = self.Compare2Images(imgA_xform, imgB)
        if "B-06" in self.rpm.name:
            print "    Rotation CW: ", diff
            imgA_xform.show()
        if diff < least_diff:
            least_diff = diff
            best_transform = "Rotation90CCW"
        
        # Reflection
        # Vertical reflection - along vertical axis
        imgA_xform = imgA.transpose(Image.FLIP_LEFT_RIGHT)
        diff = self.Compare2Images(imgA_xform, imgB)
        if "B-06" in self.rpm.name:
            print "    Reflection vertical: ", diff
            imgA_xform.show()
        if diff < least_diff:
            least_diff = diff
            best_transform = "ReflectionVertical"

        # Horizontal reflection - along horizontal axis  
        imgA_xform = imgA.transpose(Image.FLIP_TOP_BOTTOM)
        diff = self.Compare2Images(imgA_xform, imgB)
        if "B-06" in self.rpm.name:
            print "    Reflection horiz: ", diff
            imgA_xform.show()
        if diff < least_diff:
            least_diff = diff
            best_transform = "ReflectionHorizontal"  

        # And

        # OR 

   
        confidence = 1.0 - least_diff
        
        # If no transformation has a confidence greater than 99%, then this information
        # is useless. None of the simply trasforms should be attempted. It will only
        # lead to bad results
        if confidence < 0.99:
            best_transform = "NoMatch"
            confidence = 0.0
        
        return best_transform, confidence
    #end def

    # This method will run through a number of image transformations and attempt to
    # find the best solution to for a 3x3 RPM
    def Solve3x3RPM(self):

        return -1, 0.0
    #end def

    # Takes the given transforms and apply to the input images
    # Also compares to the answer choices
    def ApplyBestTransforms(self, AB_transform, AC_transform):
        answer = -1
        confidence = 0.0

        # Apply the AB transform to C
        AB_C_img = self.ApplyTransform(self.C, AB_transform)
        # See if that matches
        temp_answer, temp_diff = self.CompareGuessToAnswers(AB_C_img)
        if (1.0-temp_diff > confidence):
            answer = temp_answer
            confidence = 1.0-temp_diff

        # Apply the AC transform to B
        AC_B_img = self.ApplyTransform(self.B, AC_transform)
        # See how well that matches
        temp_answer, temp_diff = self.CompareGuessToAnswers(AC_B_img)
        if (1.0-temp_diff > confidence):
            answer = temp_answer
            confidence = 1.0-temp_diff

        # Apply AB then AC
        

        # Apply AC then AB



        return answer, confidence
    #end def

    # Apply the given transform to the given image
    def ApplyTransform(self, image, transform):
        xform_img = image 

        if transform == "NoTransformation":
            xform_img = image
        elif transform == "Rotation90CCW":
            xform_img = image.rotate(90)
        elif transform == "Rotation90CW":
            xform_img = image.rotate(270)
        elif transform == "ReflectionVertical":
            xform_img = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif transform == "ReflectionHorizontal":
            xform_img = image.transpose(Image.FLIP_TOP_BOTTOM)

        return xform_img
    #end def

    # This method takes in an image that represents a potential answer
    # Returns a value between 0 and 1 that represent the similarity along with the index
    # of the best match
    def CompareGuessToAnswers(self, guess):
        diff = 1.0 
        best_match = -1

        if(self.rpm.problemType == "2x2"):
            for i in range(1,7):
                # Find the percent difference between guess and answer
                temp_diff = self.Compare2Images(guess, self.answers[str(i)])
                
                if temp_diff < diff:
                    best_match = i
                    diff = temp_diff     
            #end for
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

        # TODO Do some cleanup to the image here
        # Some of the images don't perfectly line up so when the difference is taken there 
        # are some artifacts
        
        # http://codereview.stackexchange.com/questions/55902/fastest-way-to-count-non-zero-pixels-using-python-and-pillow
        num_pixels_diff = 0
        bbox = img_diff.getbbox()
        if not bbox: 
            num_pixels_diff = 0
        else: 
            num_pixels_diff = sum(img_diff.crop(bbox)
               .point(lambda x: 255 if x else 0)
               .convert("L")
               .point(bool)
               .getdata())

        # Calculate the percentage
        diff_percentage = float(num_pixels_diff)/img_diff_size  

        return diff_percentage
    #end def

    
    # Finds the absolute value difference between two images
    def FindImageDifference(self, imgA, imgB):
        img_diff = ImageChops.difference(imgA, imgB)
        return img_diff
    #end def

    # Handles cases where a simple transformation doesn't work
    def HandleNoMatch(self, AB_xform, AC_xform):
        confidence = 0.0
        best_answer = -1

        # Find image differences
        AB_diff = ImageChops.difference(self.A, self.B)
        AC_diff = ImageChops.difference(self.A, self.C)

        # Break into cases
        # If AB doesn't have a match and AC does
        if AB_xform == "NoMatch" and AC_xform != "NoMatch":
            # Apply the transformation from A to C to AB difference
            AB_diff_xform = self.ApplyTransform(AB_diff, AC_xform)

            # Add AB diff xform to C image
            C_AB_diff_xform = ImageChops.add(self.C, AB_diff_xform)

            # TODO: I might need a difference as well. It could be the case
            # that A has something that B does not, so B removes something
            # from A

            # Compare to answers
            best_answer, confidence = self.CompareGuessToAnswers(C_AB_diff_xform)

        # If AB has a match and AC does not
        elif AB_xform != "NoMatch" and AC_xform == "NoMatch":
            # Apply AB xform to AC image difference
            AC_diff_xform = self.ApplyTransform(AC_diff, AB_xform)

            # Add AC xform to B image
            B_AC_diff_xform = ImageChops.add(self.B, AC_diff_xform)

            # Compare to answers
            best_answer, confidence = self.CompareGuessToAnswers(B_AC_diff_xform)

        # If neither AB nor AC have a match
        elif AB_xform == "NoMatch" and AC_xform == "NoMatch":
            best_answer = -1

        # If both have a match don't do anything. Handled by simply transforms
        
        return best_answer, confidence
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
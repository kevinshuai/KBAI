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
from PIL import Image
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

        print problem.name
        print problem.problemType
        print problem.figures["A"].visualFilename
        

        if problem.problemType == "2x2":
            best_answer, best_confidence_rating = self.Solve2x2RPM()
        elif problem.problemType == "3x3":
            best_answer, best_confidence_rating = self.Solve3x3RPM()



        return best_answer
    #end def

    # This method will run through a number of image transformations and attempt to
    # find the best solution to for a 2x2 RPM
    # Find the best transformation between A and B and between A and C. Then apply those
    # transformations to from C to D and from B to D 
    def Solve2x2RPM(self):
        best_answer = -1
        best_confidence = 0.0

        # No transformation - just take A
        best_match, confidence = self.CompareGuessToAnswers(self.rpm.figures["A"])
        if confidence > best_confidence:
            best_answer = best_match
            best_confidence = confidence

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
 
        return best_match, diff
    #end def

#end class
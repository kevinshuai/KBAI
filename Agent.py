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

    NO_DIFF = 0.0

    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        self.sizes = [ "very small", "small", "medium", "large", "very large", "huge"]
        self.figures_3x3 = [ "A", "B", "C", "D", "E", "F", "G", "H" ] 
        self.answers_3x3 = [ "1", "2", "3", "4", "5", "6", "7", "8" ]
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

            print "  Answer: ", best_answer, " Confidence: ", best_confidence_rating
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

        # Find A to C transformation
        best_AC_transformation, AC_confidence = self.FindA2CTransform()

        # Apply given transforms and compare to answers, returning best one
        simple_answer, simple_confidence = self.ApplyBestTransforms(best_AB_transformation, best_AC_transformation)  

        # The above methods allow for simple transformations between A and B and A and C
        # This essentially treats them as separate 2x1 problems which are then combined later
        # This works for many problems but not all. Sometimes a more complicated transformation is
        # required. These will be handled here
        complex_answer, complex_confidence = self.HandleNoMatch(best_AB_transformation, best_AC_transformation)

        # If the simple transformation has a NoMatch and the complex confidence is pretty close to 
        # the simple confidence, favor the complex confidence
        if best_AB_transformation == "NoMatch" or best_AC_transformation == "NoMatch":          
            # If the two are about the same, favor complex
            if FuzzyCompare(complex_confidence, simple_confidence):
                best_answer = complex_answer
                confidence = complex_confidence
            elif complex_confidence > simple_confidence:
                best_answer = complex_answer
                confidence = complex_confidence
            else:
                best_answer = simple_answer
                confidence = simple_confidence
        # If there are two matches, just keep it simple
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
        diff = Compare2Images(imgA_xform, imgB)
        if diff < least_diff:
            least_diff = diff
            best_transform = "NoTransformation"

        # Rotation
        # 90 CCW
        imgA_xform = imgA.rotate(90)
        diff = Compare2Images(imgA_xform, imgB)
        
        if diff < least_diff:
            least_diff = diff
            best_transform = "Rotation90CW"

        # 90 CW
        imgA_xform = imgA.rotate(270)
        diff = Compare2Images(imgA_xform, imgB)
        
        if diff < least_diff:
            least_diff = diff
            best_transform = "Rotation90CCW"
        
        # Reflection
        # Vertical reflection - along vertical axis
        imgA_xform = imgA.transpose(Image.FLIP_LEFT_RIGHT)
        diff = Compare2Images(imgA_xform, imgB)
        
        if diff < least_diff:
            least_diff = diff
            best_transform = "ReflectionVertical"

        # Horizontal reflection - along horizontal axis  
        imgA_xform = imgA.transpose(Image.FLIP_TOP_BOTTOM)
        diff = Compare2Images(imgA_xform, imgB)
        
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
        '''
        I think I need to move from specific to general. If I have too general of a method
        I will have false positives. If I have a unique solution to a problem it should go
        first
        '''

        # Case Basic C-01 and D-01: both rows are equal. Look for answer identical to any image in third row
        if self.EqualAlongFirstTwoRows():
            guess_img =  self.G.copy()
            answer, diff = self.CompareGuessToAnswers(guess_img)
            print self.rpm.name, " Equal along first 2 rows"
            return answer, 1.0-diff

        # Basic C-11, C-12
        # If difference between A and B is equal to the difference between D and E is equal to the difference between G and H
        if IsDifferenceSameAcrossRows(self.questions):
            EF_diff = ImageChops.difference(self.E, self.F)
            guess = ImageChops.subtract(self.H, EF_diff)
            answer, diff = self.CompareGuessToAnswers(guess)
            print self.rpm.name, " Difference same across rows"
            return answer, 1.0-diff

        # Case Basic C-07: Moving circle, stationary diamond
        # This one has image transformations that can be used
        # If D and F are vertical reflections and B and H are horizontal reflections and C and G are 180 rotation
        # Then ? is a 180 rotation of A
        if IsVerticalReflection(self.D, self.F) and IsHorizontalReflection(self.B, self.H) and Is180Rotation(self.C, self.G):
            guess = self.A.copy().rotate(180)
            answer, diff = self.CompareGuessToAnswers(guess)
            if FuzzyCompare(diff, 0.0, 0.02):
                print self.rpm.name, " Basic C-07"
                return answer, 1.0-diff
        
        # Case Basic C-08: Filled/Unfilled squares
        # If B and D are 90 CW rotation and C and G are same and F and H are 90 CCW rotation, rotate F or H and AND rotated images
        # TODO: This matchs C-02. Find a way to solve C-02 before reaching this code (or just take the hit)
        if Is90CWRotation(self.B, self.D) and FuzzyAreImagesEqual(self.C, self.G) and Is90CCWRotation(self.F, self.H):
            # Rotate F 90 degrees CW
            rotatedF = self.F.copy().rotate(270)
            rotatedF = rotatedF.convert("1")
            binaryH = self.H.copy().convert("1")
            guess = ImageChops.logical_or(rotatedF, binaryH)
            guess = guess.convert("RGBA")
            guess_blur = guess.filter(ImageFilter.MinFilter())            
            answer, diff = self.CompareGuessToAnswers(guess_blur)
            if FuzzyCompare(diff, 0.0, 0.05):
                print self.rpm.name, " Basic C-08"
                return answer, 1.0-diff

        # Case Basic D-02: Shifting shapes - right
        # Case Basic D-03
        # Case Basic D-11
        if IsRightShift(self.questions):
            guess = self.A
            answer, diff = self.CompareGuessToAnswers(guess)
            print self.rpm.name, " Basic shift right"
            return answer, 1.0-diff
        
        # Case Basic C-02: Growing square
        # I don't have a good way to handle this. I need a way to create a new image rather
        # than just manipulate an existing one. This is hard to do since I don't know what is
        # guaranteed on the out of sample set.
        # Maybe consult the verbal description
        # ImageDraw

        # Case Basic C-03: Multiplying diamonds
        #if "Basic Problem C-03" in self.rpm.name:
        #   img = FindImageSameness(self.A, self.B)
        #   img.show()

        # Case Basic D-06: Shift right with sameness along row
        # Find sameness along a row. Remove sameness from a row to get a shape. Determine
        # if that shape shifts. If so, take sameness along bottom row and shifted image. 
        AB_same = FindImageSameness(self.A, self.B)
        BC_same = FindImageSameness(self.B, self.C)
        DF_same = FindImageSameness(self.D, self.F)
        EF_same = FindImageSameness(self.E, self.F)
        if FuzzyAreImagesEqual(AB_same, BC_same) and FuzzyAreImagesEqual(DF_same, EF_same):
            # We have established there is a pattern along rows
            # Now we need to see if the pattern shifts right
            BF_same = FindImageSameness(self.B, self.F)
            FG_same = FindImageSameness(self.F, self.G)
            if FuzzyAreImagesEqual(BF_same, self.F) and FuzzyAreImagesEqual(FG_same, self.G):
                CD_same = FindImageSameness(self.C, self.D)
                DH_same = FindImageSameness(self.D, self.H)
                if FuzzyAreImagesEqual(CD_same, self.D) and FuzzyAreImagesEqual(DH_same, self.H):
                    GH_same = FindImageSameness(self.G, self.H)
                    AB_xor = FindImageXOR(self.A, self.B)                    
                    guess = ImageChops.difference(GH_same, AB_xor)
                    answer, diff = self.CompareGuessToAnswers(guess)
                    print self.rpm.name, " Pattern along row, shift right"
                    return answer, 1.0-diff
                
        # Case Basic C-05: Star with circles
        # An AND of the images might work. 
        # This also has some false positives. Might need to move it further down        
        guess = self.LogicalANDOfAllQuestions()
        answer, diff = self.CompareGuessToAnswers(guess.convert("RGBA"))
        if FuzzyCompare(diff, 0.0, 0.03):
            print self.rpm.name, " AND of all questions"
            return answer, 1.0-diff

        # Case Basic C-04: Intersecting circles
        # Case Basic C-06
        # Again, it looks like I would have to synthesize the answer
        # Here I can cheat a little bit. All the answers but one appear in the problem itself
        # I can simply choose the answer that does not appear in the question      
        guess, confidence = self.AllAnswersAppearInProblemButOne()
        if guess != -1:
            print self.rpm.name, " All answers appear in problem but one"
            return guess, confidence 


        # Right here is where I can test for C-02, C-03, and C-04
        # These have verbal descriptions and I can't think of a way to
        # solve them visually. They all match the BisectAndSwap case, so their tests
        # need to be before that one. 
        if self.rpm.hasVerbal:
            # C-02
            # If the number of objects in each figure is the same
            # and one of those objects is the same amongst all of them
            # If each figure in adjacent columns has a shape that is one step larger
            # than the previous one
            # Choose answer that has the same element and the figure that is one larger
            # (I feel like this will be a lot of for loops)
            num_objects = len(self.rpm.figures["A"].objects)
            num_objects_same = True
            for figure_name in self.figures_3x3:
                figure = self.rpm.figures[figure_name]

                num_objects_same = (num_objects == len(figure.objects)) and num_objects_same
            #end for

            # If the number of objects is the same
            if num_objects_same:
                # Find the common object
                common_object = 0
                for object_name_A in self.rpm.figures["A"].objects:
                    for object_name_B in self.rpm.figures["B"].objects:
                        objectA = self.rpm.figures["A"].objects[object_name_A]
                        objectB = self.rpm.figures["B"].objects[object_name_B]

                        # If all the attributes are equal, then we have found the common object 
                        if AreObjectAttributesEqual(objectA, objectB):
                            common_object = objectA
                #end for

                # Now that the common object has been found, look for the answer
                for answer_name in self.answers_3x3:
                    answer = self.rpm.figures[answer_name]

                    # If the number of objects agrees
                    if num_objects == len(answer.objects):
                        # Go through each object
                        contains_huge = False
                        contains_common_object = False
                        for object_name in answer.objects:
                            object = answer.objects[object_name]
                            
                            if AreObjectAttributesEqual(common_object, object):
                                contains_common_object = True

                            if "size" in object.attributes and object.attributes["size"] == "huge":
                                contains_huge = True
                        #end for

                        if contains_common_object and contains_huge:
                            answer = int(answer_name)
                            confidence = 1.0
                            return answer, confidence


            #end if

            # C-03, C-04
            # If the shapes of all objects in all the figures are the same
            # Count the number of objects. It is the number of objects in the first 
            # figure in the row times the column number. 1, 2, 3; 2, 4, 6; 3, 6, 9
            # If this pattern holds for the first two rows, look for the answer appropriately
            all_shapes_same = True
            shape = self.rpm.figures["A"].objects["a"].attributes["shape"]

            for figure_name in self.figures_3x3:
                figure = self.rpm.figures[figure_name]

                for object_name in figure.objects:
                    obj = figure.objects[object_name]
                    all_shapes_same = (shape == obj.attributes["shape"]) and all_shapes_same
            #end for

            if (len(self.rpm.figures["B"].objects) == 2*len(self.rpm.figures["A"].objects)) and (len(self.rpm.figures["C"].objects) == 3*len(self.rpm.figures["A"].objects)):
                if (len(self.rpm.figures["E"].objects) == 2*len(self.rpm.figures["D"].objects)) and (len(self.rpm.figures["F"].objects) == 3*len(self.rpm.figures["D"].objects)):
                    # We have established a pattern. Now find the answer that matches the shape and the number of objects that should be present. 
                    num_objects = 3*len(self.rpm.figures["G"].objects)
                    
                    for answer_name in self.answers_3x3:
                        answer = self.rpm.figures[answer_name]
                        
                        answer_shapes_match_original_shape = True
                        for object_name in answer.objects:
                            obj = answer.objects[object_name]
                            answer_shapes_match_original_shape = (shape == obj.attributes["shape"]) and answer_shapes_match_original_shape

                        if answer_shapes_match_original_shape:
                            if num_objects == len(answer.objects):
                                answer = int(answer_name)
                                confidence = 1.0

                                return answer, confidence
            #end if

        # Case Basic C-09: Travelling triangles/stars
        # Bisect image. Combine image with halves swapped
        # This might need cleaned up a bit. It answers too many incorrectly
        guess = BisectAndSwap(self.G)
        answer, diff = self.CompareGuessToAnswers(guess)
        # This is really fuzzy. It needs moved to the bottom
        if FuzzyCompare(diff, 0.0, 0.09):
            print self.rpm.name, " Bisect and swap"
            return answer, 1.0-diff

        # Case Basic C-10: Multiplying spreading diamonds
        # B and D are rotations, C and G are rotations, F and H are rotations
        # Split C or G in half. Refection to get complete diamond, crop to get only the diamond
        # Combine new halves to get solution

        # Case Basic D-04: 
        # Case Basic D-05
        AB_same = FindImageSameness(self.A, self.B)
        BC_same = FindImageSameness(self.B, self.C)
        if FuzzyAreImagesEqual(AB_same, BC_same):
            AD_same = FindImageSameness(self.A, self.D)
            DG_same = FindImageSameness(self.D, self.G)
            if FuzzyAreImagesEqual(AD_same, DG_same):
                GH_same = FindImageSameness(self.G, self.H)
                CF_same = FindImageSameness(self.C, self.F)
                guess = ImageChops.logical_and(GH_same, CF_same)
                answer, diff = self.CompareGuessToAnswers(guess)
                print self.rpm.name, " Pattern along row and column"
                return answer, 1.0-diff
                
        # Case Basic D-07: Shift left with shift right
        # Find sameness between A and E. That is one part of the answer. Find
        # sameness between B, F, and G. Remove sameness from B. Take this and 
        # combine with sameness between A and E to generate answer.
        # Covered by all answers appear in problem but one (?)

        # Case Basic D-08: Shift left, shift right, shift right
        # Shapes are shifting left, outer shape is shifting right, unfill is shifting right
        # I might have to dig into the RavensObject to look for a 'filled' object
        # I don't see a way to solve this visually. There is only 1 filled diamond here
        # and I can't find a way to extract just the filled diamond

        # Case Basic D-09: shift left, shift right
        # Inner pattern shifts right. Outer shape shifts left
        # Find sameness between shifts. Combine to generate answer
        # All answers appear in problem but one (?)

        # Case Basic D-10: Shift left, shift right
        # Inner shape shifts right, additional pattern shifts left
        # Find sameness between shifts. Combine to generate answer
        BF_same = FindImageSameness(self.B, self.F)
        BG_same = FindImageSameness(self.B, self.G)
        CD_same = FindImageSameness(self.C, self.D)
        DH_same = FindImageSameness(self.D, self.H)
        if FuzzyAreImagesEqual(BF_same, BF_same) and FuzzyAreImagesEqual(CD_same, DH_same):
            # We have established there is a shift right
            # Now see if there is a shift left
            AF_same = FindImageSameness(self.A, self.F)
            FH_same = FindImageSameness(self.F, self.H)
            CG_same = FindImageSameness(self.C, self.G)
            EG_same = FindImageSameness(self.E, self.G)
            if FuzzyAreImagesEqual(AF_same, FH_same) and FuzzyAreImagesEqual(CG_same, EG_same):
                # We have established there is a shift left
                # We need to combine the two in order to form an answer
                AE_same = FindImageSameness(self.A, self.E)
                BD_same = FindImageSameness(self.B, self.D)
                guess = FindLogicalAND(AE_same, BD_same)
                answer, diff = self.CompareGuessToAnswers(guess)
                return answer, 1.0-diff

        # Case Basic D-12: Shifting shapes and counts
        # I don't think I can solve this visually. It requires counting the number
        # of shapes that are present which is simply not possible this this project
        # I think the only way to solve this in a reasonable timeframe
        # is with verbal descriptions

        return -1, 0.0
    #end def

    #***************************************************************************************
    # Takes the given transforms and apply to the input images
    # Also compares to the answer choices
    #***************************************************************************************
    def ApplyBestTransforms(self, AB_transform, AC_transform):
        answer = -1
        answer1 = -1
        answer2 = -1
        answer3 = -1
        answer4 = -1

        confidence = 0.0
        confidence1 = 0.0
        confidence2 = 0.0
        confidence3 = 0.0
        confidence4 = 0.0
        
        # Apply the AB transform to C
        AB_C_img = ApplyTransform(self.C, AB_transform)
        # See if that matches
        answer1, temp_diff = self.CompareGuessToAnswers(AB_C_img)
        confidence1 = 1.0-temp_diff

        # Apply the AC transform to B
        AC_B_img = ApplyTransform(self.B, AC_transform)
        # See how well that matches
        answer2, temp_diff = self.CompareGuessToAnswers(AC_B_img)
        confidence2 = 1.0 - temp_diff

        # TODO: Apply AB then AC
        

        # TODO: Apply AC then AB

        # Pick the answer with the highest confidence value with some 
        # wiggle room
        if FuzzyCompare(confidence1, confidence2):
            # Eliminate answers where there aren't good matches
            if AB_transform == "NoMatch":
                answer = answer2
                confidence = confidence2
            elif AC_transform == "NoMatch":
                answer = answer1
                confidence = confidence1
            # If both have transforms, arbitrarily pick the AB one to dominate
            else:
                answer = answer1
                confidence = confidence1
        elif confidence1 > confidence2:
            answer = answer1
            confidence = confidence1
        elif confidence2 > confidence1:
            answer = answer2
            confidence = confidence2            

        return answer, confidence
    #end def

    #***************************************************************************************
    # This method takes in an image that represents a potential answer
    # Returns a value between 0 and 1 that represent the similarity along with the index
    # of the best match
    #***************************************************************************************
    def CompareGuessToAnswers(self, guess):
        diff = 1.0 
        best_match = -1

        if(self.rpm.problemType == "2x2"):
            for i in range(1,7):
                # Find the percent difference between guess and answer
                temp_diff = Compare2Images(guess, self.answers[str(i)])
                
                if temp_diff < diff:
                    best_match = i
                    diff = temp_diff     
            #end for
        elif(self.rpm.problemType == "3x3"):
            for i in range(1,9):
                # Find the percent difference between guess and answer
                temp_diff = Compare2Images(guess, self.answers[str(i)])
                
                if temp_diff < diff:
                    best_match = i
                    diff = temp_diff 
            #end for
        #end if

        return best_match, diff
    #end def
    
    # Finds the absolute value difference between two images
    def FindImageDifference(self, imgA, imgB):
        img_diff = ImageChops.difference(imgA, imgB)
        return img_diff
    #end def

    #***************************************************************************************
    # Handles cases where a simple transformation doesn't work
    #***************************************************************************************
    def HandleNoMatch(self, AB_xform, AC_xform):
        max_confidence = 0.0
        best_answer = -1      

        # Find image differences
        # This is absolute difference, so I will have to try addition and subtraction
        AB_diff = ImageChops.difference(self.A, self.B)
        AC_diff = ImageChops.difference(self.A, self.C)

        # Break into cases
        # If AB doesn't have a match and AC does
        if AB_xform == "NoMatch" and AC_xform != "NoMatch":
            # Apply the transformation from A to C to AB difference
            AB_diff_xform = ApplyTransform(AB_diff, AC_xform)

            # Add AB diff xform to C image
            C_AB_diff_xform = ImageChops.add(self.C, AB_diff_xform)

            # Compare to answers
            answer_add, confidence_add = self.CompareGuessToAnswers(C_AB_diff_xform)

            # TODO: I might need a difference as well. It could be the case
            # that A has something that B does not, so B removes something
            # from A
            
            # Subtract AB_diff xform from C image
            C_AB_diff_xform = ImageChops.subtract(self.C, AB_diff_xform)

            # Compare to answers
            answer_sub, confidence_sub = self.CompareGuessToAnswers(C_AB_diff_xform)

            # Pick the one with greatest confidence
            if confidence_add > confidence_sub:
                best_answer = answer_add
                _max_confidence = confidence_add
            else:
                best_answer = answer_sub
                max_confidence = confidence_sub            

        # If AB has a match and AC does not
        elif AB_xform != "NoMatch" and AC_xform == "NoMatch":
            # Apply AB xform to AC image difference
            AC_diff_xform = ApplyTransform(AC_diff, AB_xform)

            # Add AC xform to B image
            B_AC_diff_xform = ImageChops.add(self.B, AC_diff_xform)

            # Compare to answers
            answer_add, confidence_add = self.CompareGuessToAnswers(B_AC_diff_xform)

            # Do same for subtracting
            B_AC_diff_xform = ImageChops.subtract(self.B, AC_diff_xform)

            # Compare to answers
            answer_sub, confidence_sub = self.CompareGuessToAnswers(B_AC_diff_xform)

            # Pick the one with greatest confidence
            if confidence_add > confidence_sub:
                best_answer = answer_add
                max_confidence = confidence_add
            else:
                best_answer = answer_sub
                max_confidence = confidence_sub             

        # If neither AB nor AC have a match
        elif AB_xform == "NoMatch" and AC_xform == "NoMatch":
            # There are a lot of combinations here. I am going to only do a few
            answer_list = []
            confidence_list = []
                        
            # Combo 1
            # Take AB difference, add to C
            C_plus_AB_diff = ImageChops.add(self.C, AB_diff)           

            # Take AC difference, add to B
            B_plus_AC_diff = ImageChops.add(self.B, AC_diff)

            # Add two images
            guess = ImageChops.add(C_plus_AB_diff, B_plus_AC_diff)

            # Find closest match to anwswer
            answer, diff = self.CompareGuessToAnswers(guess)
            answer_list.append(answer)
            confidence_list.append(1.0-diff)

            # Combo 2
            # Try just the individual additions
            answer, diff = self.CompareGuessToAnswers(C_plus_AB_diff)
            answer_list.append(answer)
            confidence_list.append(1.0-diff)

            answer, diff = self.CompareGuessToAnswers(B_plus_AC_diff)
            answer_list.append(answer)
            confidence_list.append(1.0-diff)

            # Combo 3
            # Subtract the differences
            C_minus_AB_diff = ImageChops.subtract(self.C, AB_diff)
            B_minus_AC_diff = ImageChops.subtract(self.B, AC_diff)   

            answer, diff = self.CompareGuessToAnswers(C_minus_AB_diff)
            answer_list.append(answer)
            confidence_list.append(1.0-diff)

            answer, diff = self.CompareGuessToAnswers(B_minus_AC_diff) 
            answer_list.append(answer)
            confidence_list.append(1.0-diff)
                        
            # Find max confidence and best answer
            max_confidence = max(confidence_list)
            best_answer = answer_list[confidence_list.index(max_confidence)]
            
        # If both have a match don't do anything. Handled by simply transforms
                
        return best_answer, max_confidence
    #end def

    #********************************************************************
    # Method to determine if the first two rows of the RPM are the same
    #******************************************************************** 
    def EqualAlongFirstTwoRows(self):
        if FuzzyAreImagesEqual(self.A, self.B, 0.05) and FuzzyAreImagesEqual(self.B, self.C, 0.02) and FuzzyAreImagesEqual(self.A, self.C, 0.05):
            if FuzzyAreImagesEqual(self.D, self.E, 0.03) and FuzzyAreImagesEqual(self.E, self.F, 0.03) and FuzzyAreImagesEqual(self.D, self.F, 0.02):
                return True

        return False

    #********************************************************************
    # Determines if all the given answer choices appear in the problem except 
    # for one. If so, the odd answer out is returned. Otherwise, return -1
    #********************************************************************
    def AllAnswersAppearInProblemButOne(self):
        possibleAnswers = [1, 2, 3, 4, 5, 6, 7, 8]
        answer = -1
        confidence = 0.0

        for i in range(0,8):
            for j in range(0,8):
                if FuzzyAreImagesEqual(self.questions[i], self.answerList[j], 0.05):
                    # Remove j from list of possible answers
                    if (j+1) in possibleAnswers:
                        possibleAnswers.remove(j+1)
        #end for

        if len(possibleAnswers) == 1:
            answer = possibleAnswers[0]
            confidence = 1.0

        return answer, confidence

    #********************************************************************
    # Finds difference of all the questions in the RPM
    #********************************************************************
    def LogicalANDOfAllQuestions(self):
        and_img = self.questions[0].convert("1")

        for i in range(1,8):
            temp_img = self.questions[i].convert("1")
            and_img = ImageChops.logical_and(and_img, temp_img)
           
        return and_img

    #********************************************************************
    # Opens and saves all the figures for a 2x2 RPM
    #********************************************************************
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

    #********************************************************************
    # Opens and saves all the figures for a 3x3 RPM
    #********************************************************************
    def Open3x3Figures(self):
        # Initialize all the images
        self.A = Image.open(self.rpm.figures["A"].visualFilename)
        self.B = Image.open(self.rpm.figures["B"].visualFilename)
        self.C = Image.open(self.rpm.figures["C"].visualFilename)
        self.D = Image.open(self.rpm.figures["D"].visualFilename)
        self.E = Image.open(self.rpm.figures["E"].visualFilename)
        self.F = Image.open(self.rpm.figures["F"].visualFilename)
        self.G = Image.open(self.rpm.figures["G"].visualFilename)
        self.H = Image.open(self.rpm.figures["H"].visualFilename)
        self.A1 = Image.open(self.rpm.figures["1"].visualFilename)
        self.A2 = Image.open(self.rpm.figures["2"].visualFilename)
        self.A3 = Image.open(self.rpm.figures["3"].visualFilename)
        self.A4 = Image.open(self.rpm.figures["4"].visualFilename)
        self.A5 = Image.open(self.rpm.figures["5"].visualFilename)
        self.A6 = Image.open(self.rpm.figures["6"].visualFilename)
        self.A7 = Image.open(self.rpm.figures["7"].visualFilename)
        self.A8 = Image.open(self.rpm.figures["8"].visualFilename)

        self.answers = {"1": self.A1,
                        "2": self.A2,
                        "3": self.A3,
                        "4": self.A4,
                        "5": self.A5,
                        "6": self.A6,
                        "7": self.A7,
                        "8": self.A8 }

        self.questions = [self.A, self.B, self.C, self.D, self.E, self.F, self.G, self.H ]
        self.answerList = [self.A1, self.A2, self.A3, self.A4, self.A5, self.A6, self.A7, self.A8 ]
    #end def
#end class
#********************************************************************
#********************************************************************


#********************************************************************
# A method to compare two values with some "fuzzy" factor
# Returns true of the values are approximately equal
# Otherwise returns false
#********************************************************************
def FuzzyCompare(value1, value2, fuzz_factor = 0.05):
    
    if value1 > value2 - fuzz_factor and value1 < value2 + fuzz_factor:
        return True

    return False

#********************************************************************
# Compares two images, returns a percentage of pixels different
#********************************************************************
def Compare2Images(imgA, imgB):
    # Find the absolute difference between the two images
    img_diff = ImageChops.difference(imgA.convert("RGBA"), imgB.convert("RGBA"))

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
        #img_diff.crop(bbox).show()
        num_pixels_diff = sum(img_diff.crop(bbox)
            .point(lambda x: 255 if x else 0)
            .convert("L")
            .point(bool)
            .getdata())

    # Calculate the percentage
    diff_percentage = float(num_pixels_diff)/img_diff_size  

    return diff_percentage
#end def

#********************************************************************
# Compares two images. If they are about equal returns true
# If they are more different than the fuzz factor, return false
#********************************************************************
def FuzzyAreImagesEqual(imgA, imgB, fuzz_factor=0.02):
    no_diff = 0.0

    diff = Compare2Images(imgA, imgB)

    if FuzzyCompare(diff, no_diff, fuzz_factor):
        return True

    return False

#********************************************************************
# Apply the given transform to the given image
#********************************************************************
def ApplyTransform(image, transform):
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

#*******************************************************************************
# Returns true of imgA is a horizontal reflection of imgB
#*******************************************************************************
def IsHorizontalReflection(imgA, imgB, fuzz_factor=0.02):
    imgB_reflection = imgB.copy().transpose(Image.FLIP_TOP_BOTTOM)

    if FuzzyAreImagesEqual(imgA, imgB_reflection, fuzz_factor):
        return True

    return False

#********************************************************************************
# Returns true if imgA is a vertical reflection of imgB
#********************************************************************************
def IsVerticalReflection(imgA, imgB, fuzz_factor=0.02):
    imgB_reflection = imgB.copy().transpose(Image.FLIP_LEFT_RIGHT)

    if FuzzyAreImagesEqual(imgA, imgB_reflection, fuzz_factor):
        return True

    return False

#*******************************************************************************
# Returns true if imgA is a 180 degree rotation of imgB
#*******************************************************************************
def Is180Rotation(imgA, imgB, fuzz_factor=0.02):
    imgB_rotation = imgB.copy().rotate(180)

    if FuzzyAreImagesEqual(imgA, imgB_rotation, fuzz_factor):
        return True

    return False

#*******************************************************************************
# Returns true if imgA is a 90 degree CW rotation of imgB
#*******************************************************************************
def Is90CWRotation(imgA, imgB, fuzz_factor=0.02):
    imgA_rotation = imgA.copy().rotate(270)

    if FuzzyAreImagesEqual(imgA_rotation, imgB, fuzz_factor):
        return True

    return False

#*******************************************************************************
# Returns true if imgA is a 90 degree CCW rotation of imgB
#*******************************************************************************
def Is90CCWRotation(imgA, imgB, fuzz_factor=0.02):
    imgA_rotation = imgA.copy().rotate(90)

    if FuzzyAreImagesEqual(imgA_rotation, imgB, fuzz_factor):
        return True

    return False

#*******************************************************************************
# Bisects the given image along the vertical axis, swaps the halves, and combines
# halves. Returns recombined image
#*******************************************************************************
def BisectAndSwap(image):
    img_copy = image.copy()

    width = img_copy.size[0]
    height = img_copy.size[1]

    bbox_left = (0, 0, width/2, height)
    left_half = img_copy.crop(bbox_left)

    bbox_right = (width/2, 0, width, height)
    right_half = img_copy.crop(bbox_right)

    swap_img = Image.new("RGBA", (width, height))
    swap_img.paste(right_half, bbox_left)
    swap_img.paste(left_half, bbox_right)

    return swap_img

#*******************************************************************************
# Returns true if the difference along the rows across columns is all the same
# In other words, if A-B == D-E, etc.
#*******************************************************************************
def IsDifferenceSameAcrossRows(questions):
    AB_diff = ImageChops.difference(questions[0], questions[1])
    BC_diff = ImageChops.difference(questions[1], questions[2])
    DE_diff = ImageChops.difference(questions[3], questions[4])
    EF_diff = ImageChops.difference(questions[4], questions[5])
    GH_diff = ImageChops.difference(questions[6], questions[7])

    if FuzzyAreImagesEqual(AB_diff, DE_diff) and FuzzyAreImagesEqual(AB_diff, GH_diff) and FuzzyAreImagesEqual(DE_diff, GH_diff):
       if FuzzyAreImagesEqual(BC_diff, EF_diff):
           return True

    return False

#*******************************************************************************
# Method to determine if set of images represents a circular right shift
# Image images are a right shift, return true. Otherwise return false
#*******************************************************************************
def IsRightShift(questions):

    if FuzzyAreImagesEqual(questions[0], questions[4], 0.05):
        if FuzzyAreImagesEqual(questions[1], questions[5], 0.05) and FuzzyAreImagesEqual(questions[1], questions[6], 0.05) and FuzzyAreImagesEqual(questions[5], questions[6], 0.05):
            if FuzzyAreImagesEqual(questions[2], questions[3], 0.05) and FuzzyAreImagesEqual(questions[2], questions[7], 0.05) and FuzzyAreImagesEqual(questions[3], questions[7], 0.05):
                return True

    return False

#***************************************************************************************
# Method to determine sameness (what is the same) between two images
# Returns an image that is white? for common areas and black(?) for difference areas
#***************************************************************************************
def FindImageSameness(imgA, imgB):

    tempA = imgA.convert("1")
    tempB = imgB.convert("1")

    # Simply applying AND results in similar areas being white and difference areas being black
    
    return ImageChops.logical_or(tempA, tempB)

#****************************************************************************************
# Returns XOR of two images
#****************************************************************************************
def FindImageXOR(imgA, imgB):
    tempA = imgA.convert("1")
    tempB = imgB.convert("1")

    return ImageChops.logical_xor(tempA, tempB)

#****************************************************************************************
# Logical and of two images
#****************************************************************************************
def FindLogicalAND(imgA, imgB):
    tempA = imgA.convert("1")
    tempB = imgB.convert("1")

    return ImageChops.logical_and(tempA, tempB)


#****************************************************************************************
# Compare object attributes
#****************************************************************************************
def AreObjectAttributesEqual(objA, objB):

    # Compare attributes
    attributes_equal = True
    keys = objA.attributes.keys()
    for key in keys:
        if key in objB.attributes:
            attibutes_equal = (objA.attributes[key] == objB.attributes[key]) and attributes_equal
        else:
            # If an attribute is not present, the objects can't be equal
            attributes_equal = False

    keys = objB.attributes.keys()
    for key in keys:
        if key in objA.attributes:
            attibutes_equal = (objA.attributes[key] == objB.attributes[key]) and attributes_equal
        else:
            # If an attribute is not present, the objects can't be equal
            attributes_equal = False

    return attributes_equal

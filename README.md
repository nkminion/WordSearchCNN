Word Search Solver:


A Python script that automatically detects and solves a Word Search puzzle from an image.



Features:

Image Preprocessing: Automatically processes an input image to isolate the puzzle and letters.

Letter Bound Detection: Finds the letters' borders using a histogram-based algorithm.

Letter Recognition: Uses a custom-trained CNN to identify the letter in each bound.

<<<<<<< HEAD
Puzzle Solver: Implements a backtracking algorithm to solve the detected puzzle. It uses a word list which removes the necessity for the user to input most words.
=======
Puzzle Solver: Implements a brute-force algorithm to solve the detected puzzle. It uses a word list which removes the necessity for the user to input most words.
>>>>>>> a19d043e (Added README)



Current Limitations:

Straight Images Only: The current version of the grid detection works best on images that are straight and un-rotated. Support for perspective warping is a potential future improvement.

Word Length: The word list consists of words at least 5 letters long. It does not detect any words that are shorter than the limit.

Maintenance Status: This is a personal project and is not actively maintained. Updates and bug fixes may be infrequent.



Requirements:

Pillow (If you plan on creating your own dataset)

PyTorch (The TensorFlow version works but is not as good as the PyTorch version)

OpenCV

NumPy



License:

<<<<<<< HEAD
This project is licensed under the MIT License. See the LICENSE file for more details.
=======
This project is licensed under the MIT License. See the LICENSE file for more details.
>>>>>>> a19d043e (Added README)

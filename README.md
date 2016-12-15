# Algorithms (final project)

Project description:
You have to develop an algorithm that given a query image finds the “closest” entries to it on a dataset of images.

Scoring:
1) Your solution will be evaluated based on how its run-time scales with the size of the input dataset, the number of input queries and the value of K.

2) It will also be evaluated on how its memory usage scale with the input.

3) Finally, your solution will also be evaluated based on its accuracy to solve a classification task. Let us be more specific about this. We will run your final code on a folder with a dataset of images and another folder with a several query images. The images are just like described above. We will run your code on these input folders for a value of K = 9. These images fall into several category. We know the categories in which each image falls but you do not.We will read the output file produced by your program where you storedthe K files closest to each query. We will read it line by line. If the category that most frequently appears on these K files is the same category as the input file, then you get one point. Otherwise you get zero points. This will produce a total score. We will then run your code, just like described above, also for K = 1, 3, 5, 7. Your final accuracy score will the highest score you get among the values of Ktested.

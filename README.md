# CSCI 3383 Algorithms (final project)
Final Project for CSCI 3383 Algorithms by:
@nashdb @reedery @hoodr

<!-- [Danielle Nash](https://github.com/nashdb) [Ryan Reede](https://github.com/reedery) [Drew Hoo](https://github.com/hoodr) -->

Included in this repo is our final code, along with the instructions for the project, and our final paper.

### Instructions for running:
1. Clone the repo locally
    * Note: We used a linux terminal to run our executables. The normal way to run in terminal will be below the exe instructions
2. ``` cd Algorithms_final_project ```
3. To run our program:
    * ``` ./final_project_exec ./Test1/database/ ./Test1/queries/ ./Test1/output/this_is_the_output 5 ```
    * Template: path/to/exe path/to/Test/database path/to/test/queries path/to/output k
        * Where K is the number of similar images you want the program to match to each input query
4. Check the results:
    * ``` ./test_solution_exec ./Test1/output/database_decode_key ./Test1/output/queries_decode_key ./Test1/output/this_is_the_output 5 ./Test1/output/performance_file ```
    * Template: path/to/solution/exe path/to/Test/output/decode_key path/to/output/decode_queries path/to/output k path/to/output/performance_file
        * Where K is the number of similar images you want the program to match to each input query
5. If you don't feel like using the executable, just run ``` python final_project_final.py ./Test1/database/ ./Test1/queries/ ./Test1/output/this_is_the_output 5 ```
    * Note: This requires you to have numpy, lshash, and scipy locally

## Project description:
You have to develop an algorithm that given a query image finds the “closest” entries to it on a dataset of images.

## Scoring:
1. Your solution will be evaluated based on how its run-time scales with the size of the input dataset, the number of input queries and the value of K.

2. It will also be evaluated on how its memory usage scale with the input.

3. Finally, your solution will also be evaluated based on its accuracy to solve a classification task. Let us be more specific about this. We will run your final code on a folder with a dataset of images and another folder with a several query images. The images are just like described above. We will run your code on these input folders for a value of K = 9. These images fall into several category. We know the categories in which each image falls but you do not.We will read the output file produced by your program where you storedthe K files closest to each query. We will read it line by line. If the category that most frequently appears on these K files is the same category as the input file, then you get one point. Otherwise you get zero points. This will produce a total score. We will then run your code, just like described above, also for K = 1, 3, 5, 7. Your final accuracy score will the highest score you get among the values of Ktested.

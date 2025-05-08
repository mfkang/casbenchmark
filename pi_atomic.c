#include <stdio.h>
#include <omp.h>

// Function to approximate the value of PI using the atomic approach
// This function uses the numerical integration method to calculate PI
double PI_ATOMIC() {
    // Number of sub - intervals for numerical integration
    // Increasing this value can improve the accuracy of the approximation
    const int N = 10000000;  
    // Width of each sub - interval
    const double dx = 1.0 / (double)N;
    // Initialize the approximation of PI
    double pi = 0.0;

    // Uncomment the following line to enable parallel execution of the for loop
    #pragma omp parallel for
    for(int i = 0; i < N; ++i) {
        // Calculate the x - coordinate at the mid - point of the current sub - interval
        double x = ((double)i + 0.5) * dx;
        // Uncomment the following line to ensure atomic update of the 'pi' variable in a parallel environment
        #pragma omp atomic
        // Update the approximation of PI
        pi += dx / (1.0 + x * x);
    }
    // Finalize the approximation of PI
    pi *= 4.0;
    return pi;
}

int main() {
    // Call the function to get the approximation of PI
    double result = PI_ATOMIC();
    // Print the approximation of PI
    printf("Approximation of PI: %lf\n", result);
    return 0;
}

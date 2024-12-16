#include "mex.h"

double add(double x, double y) {
    return x + y;
}

void mexFunction(int nlhs, mxArray* plhs[], int nrhs, const mxArray* prhs[]) {

    double* a;
    double* b;
    double c, d;
    plhs[0] = mxCreateDoubleMatrix(1, 1, mxREAL);
    plhs[1] = mxCreateDoubleMatrix(1, 1, mxREAL);
    a = mxGetPr(plhs[0]);
    b = mxGetPr(plhs[1]);
    c = *(mxGetPr(prhs[0]));
    d = *(mxGetPr(prhs[1]));
    *a = add(c, d);
    *b = add(c, d) + 1;
}
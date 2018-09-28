# distutils: language=c++
# % # cython: profile=True
# % # cython: linetrace=True

from libcpp.string cimport string

cdef extern from "tmat.h":
    cdef cppclass tMatrix:
        tMatrix(string, string, string, string, int, float, int, int, int, int, int) except +
        int get(string, string) except +
        tMatrix() except +
        int get(char *, char *) except +


cdef class tmatrix:
    cdef tMatrix c_tmat
    def __cinit__(self, string infile, string nn_pinfile, string nn_sinfile, string outfile, int N, float impedence, int num_threads, int outer_node_rows, int outer_node_cols, int mode, int write_mode):
        self.c_tmat = tMatrix(infile, nn_pinfile, nn_sinfile, outfile, N, impedence, num_threads, outer_node_rows, outer_node_cols, mode, write_mode)

    def get(self, source, dest):
        cdef string cpp_source = str.encode(source)
        cdef string cpp_dest = str.encode(dest)
        return self.c_tmat.get(cpp_source, cpp_dest)


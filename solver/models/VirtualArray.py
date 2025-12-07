import numpy as np
from solver.utils.get_linear_index import get_linear_index

class VirtualArray:
    def __init__(self, data, virtual_size,cyclic_type="no_cyclic"):
        """
        Tạo mảng 1D nhưng giả lập mảng 2D có kích thước virtual_size :(n_row,n_col)
        """
        self.data = np.array(data, dtype=float)
        self.virtual_size = virtual_size
        n_rows, n_cols = self.virtual_size
        if self.data.size != n_rows * n_cols:
            raise ValueError("Kích thước mảng 1D không khớp với virtual_size")
        
        self.cyclic_type = cyclic_type
        self.size = self.get_length()

    def get_1D(self,index):
            if index is not None:
                return self.data[index]
            else:
                 return 0.0 
    
    def get_2D(self,position):
            index =  get_linear_index(position,self.virtual_size,self.cyclic_type)
            return self.get_1D(index)
    
   
    def get_length(self):
            return int(self.data.size)



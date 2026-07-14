import os
# Disable OneDNN/MKLDNN before PaddlePaddle loads (workaround for PaddlePaddle 3.3.x bug)
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from ui.main_window import MainWindow

if __name__ == "__main__":
    MainWindow().mainloop()

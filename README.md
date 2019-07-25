# bibfinder

批量查找bibtex的工具


必应不需要翻墙，谷歌需要先翻墙才行。
点击谷歌或必应后，将要查找的论文名称Ctrl+V粘贴到输入框里，点击确定。
接受的论文格式如下两种所示
引号包裹论文名的：
[5] H. Zhang, J. Li, Y. Huang, and L. Zhang, “A nonlocal weighted joint
sparse representation classification method for hyperspectral imagery,”
IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 7, no. 6,
pp. 2056–2065, Jun. 2014.
[6] J. Li, J. M. Bioucas-Dias, and A. Plaza, “Semisupervised hyperspectral
image segmentation using multinomial logistic regression with active
learning,” IEEE Trans. Geosci. Remote Sens., vol. 48, no. 11, pp. 4085– 
4098, Nov. 2010.

或

仅论文名，用换行符分隔的：
Noise reduction of hyperspectral imagery（换行）
using hybrid spatial-spectral derivative-domain wavelet shrinkage（换行）
（一个换行）
Hyperspectral image processing by jointly（换行）
filtering wavelet component tensor（换行）
（一个换行）
（两个换行）
（三个换行）
Hyperspectral image denoising using first order spectral roughness（换行）
penalty in wavelet domain（换行）

连续的行将被认为是同一个论文标题。空换行用来分隔不同的论文标题。

结果将复制到您的剪贴板。
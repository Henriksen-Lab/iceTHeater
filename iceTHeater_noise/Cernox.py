import cmath
from decimal import Decimal

def get_T_cernox_3(R):
    c1 = [5.5582108, -6.41962, 2.86239, -1.059453, 0.328973, 0.081621997, 0.012647, 0.00088100001, -0.001982,
          0.00099099998]
    c14 = [43.140221, -38.004025, 8.0877571, -0.913351, 0.091504, -0.0036599999, -0.0060470002]
    c80 = [177.56671, -126.69688, 22.017452, -3.116698, 0.59847897, -0.111213, 0.01663, -0.0067889998]

    if R > 665.0:
        ww1 = c1
        for i in range(0, len(c1)):
            ww1[i] = c1[i] * cmath.cos(i * cmath.acos(
                ((cmath.log10(R) - 2.77795312391) - (4.06801081354 - cmath.log10(R))) / (
                        4.06801081354 - 2.77795312391)))
        result = sum(ww1)
    elif R > 184.8:
        ww14 = c14
        for i in range(0, len(c14)):
            ww14[i] = c14[i] * cmath.cos(i * cmath.acos(
                ((cmath.log10(R) - 2.22476915988) - (2.86208992852 - cmath.log10(R))) / (
                        2.86208992852 - 2.22476915988)))
        result = sum(ww14)
    else:
        ww80 = c80
        for i in range(0, len(c80)):
            ww80[i] = c80[i] * cmath.cos(i * cmath.acos(
                ((cmath.log10(R) - 1.72528854694) - (2.3131455111 - cmath.log10(R))) / (2.3131455111 - 1.72528854694)))
        result = sum(ww80)
    return Decimal(result.real).quantize(Decimal("0.000000"))


def get_T_cernox_2(R):

    c1 = [5.570335, -6.431053, 2.856602, -1.051419, 0.323253, -0.079245, 0.012158, 0.001578]
    c14 = [43.169208, -38.016747, 8.059929, -0.902484, 0.089422, -0.001914, -0.005890]
    c80 = [177.584598, -126.694057, 21.993243, -3.117889, 0.604405, -0.115986, 0.020293, -0.008827,0.003174]

    if R > 622.2:
        ww1 = c1
        for i in range(0, len(c1)):
            ww1[i] = c1[i] * cmath.cos(i * cmath.acos(
                ((cmath.log10(R) - 2.75625968402) - (4.01509599296 - cmath.log10(R))) / (
                        4.01509599296 - 2.75625968402)))
        result = sum(ww1)
    elif R > 178.7:
        ww14 = c14
        for i in range(0, len(c14)):
            ww14[i] = c14[i] * cmath.cos(i * cmath.acos(
                ((cmath.log10(R) - 2.21079540982) - (2.83897253475 - cmath.log10(R))) / (
                        2.83897253475 - 2.21079540982)))
        result = sum(ww14)
    else:
        ww80 = c80
        for i in range(0, len(c80)):
            ww80[i] = c80[i] * cmath.cos(i * cmath.acos(
                ((cmath.log10(R) - 1.71676512287) - (2.29813864582 - cmath.log10(R))) / (2.29813864582 - 1.71676512287)))
        result = sum(ww80)
    return Decimal(result.real).quantize(Decimal("0.000000"))


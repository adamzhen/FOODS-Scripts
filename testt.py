# Top View
L = 18.1 # TOTAL LENGTH (cm)
L1 = 0.404 * L
L11 = 0.2 * L #Length from root to point
L2 = 0.78 * (L1-L11)
L12 = L1 - L11 - L2
L3 = L - L1

W = 2.71 # MAXIMUM WIDTH (cm)
W1 = 0.775 * W
Wtip = 0.0517 * W
W12 = L11/(L11+L12) * (W-W1) + W1
Wt1 = 0.54 # 2 outer tines
Wt2 = 0.46 # 2 inner tines
Ws = (W12 - 2*Wt1 - 2*Wt2) / 3 # 3 slots
W3 = 0.78
W4 = 1.3
W21 = 0.94 * (W-W3) + W3
l21 = 0.85 * L2
W22 = 0.56 * (W-W3) + W3
l22 = 0.65 * L2
W23 = 0.04 * (W-W3) + W3
l23 = 0.3 * L2
fr1 = Wtip / 3
fr2 = Ws / 2

print(W3)

# Side View 

T = 0.45 # MAXIMUM THICKNESS (cm)
T1 = 0.1

l4 = L2
h4 = 1.37 # heights expressed in terms of h4, since it's the max height
h7 = 0.33 # height of tine tip from plane
l1 = 0.27 * l4
h1 = 0.1 * h4
l2 = 0.52 * l4
h2 = 0.45 * h4
l3 = 0.72 * l4
h3 = 0.95 * h4
l5 = L1 - (L11+L12)/2
h5 = (h4 + h7) * 0.55
l6 = l5 + L11/100
h6 = h5 + (T + T1) * 0.58

# Bottom View

T2 = 0.15
T3 = 0.15

# X Support

Lx = 1.0
L4 = L3 - Lx
Tx1 = T * 0.2
Tx2 = T * 0.4
rx = 0.12
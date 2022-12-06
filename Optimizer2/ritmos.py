regueton = (
    [
        [
            [5.837291666666713, 1, 2, 0, 1.5068170704321868, 3.0989829527086985, [1.71428571428571, 2.78571428571429]],
            [5.467519199250946, 1, 1, 0, 4.483707220027799, 4.997344103215625, [4.71428571428571]],
            [5.467519199250946, 1, 1, 0, 6.197992934313519, 6.711629817501345, [6.42857142857143]]
        ],
        [
            [5.467519199250946, 1, 1, 0, 1.9122786485992298, 2.4259155317870555, [2.14285714285714]],
            [5.467519199250946, 1, 1, 0, 3.19799293431352, 3.7116298175013456, [3.42857142857143]],
            [5.467519199250946, 1, 1, 0, 5.5551357914563795, 6.0687726746442054, [5.78571428571429]],
            [5.83729166666666, 1, 2, 0, 6.649674213289335, 8.241840095565847, [1.07142857142857, 6.85714285714286]]
        ],
        [
            [5.467519199250946, 1, 1, 0, 2.7694215057420895, 3.2830583889299154, [3]],
            [5.467519199250946, 1, 1, 0, 3.6265643628849498, 4.140201246072776, [3.85714285714286]],
            [5.467519199250946, 1, 1, 0, 4.912278648599229, 5.425915531787055, [5.14285714285714]],
            [5.837291666666713, 1, 2, 0, 6.006817070432187, 7.598982952708699, [0.428571428571429, 6.21428571428571]]
        ],
        [
            [5.467519199250946, 1, 1, 0, 1.0551357914563797, 1.5687726746442057, [1.28571428571429]],
            [5.83729166666666, 1, 2, 0, 4.292531356146474, 5.884697238422987, [4.5, 5.57142857142857]]
        ]
    ]
)

claveCubana = (
    [
        [
            [5.467519199250946, 1, 1, 0, 1.6037979257420896, 2.1174348089299153, [1.83437642]]
        ], 
        [
            [6.704793529466665, 1, 2, 0, 0.99062218204726, 2.6249100226780517, [0.23219955, 1.16099773]]
        ], 
        [
            [6.57828796239222, 1, 2, 0, 1.3809500032500461, 3.0043913467936423, [0.60371882, 1.55573696]]
        ]
    ]
)

Samba = (
    [
        [
            [5.467519199250946, 1, 1, 0, 3.4381743357420893, 3.9518112189299153, [3.66875283]], 
            [5.467519199250946, 1, 1, 0, 4.25087275574209, 4.7645096389299155, [4.48145125]], 
            [5.692749210796667, 1, 2, 0, 6.123289334576631, 7.723196860831498, [6.33904762, 0.16253968]]
        ],
        [
            [5.81925477787111, 1, 2, 0, 1.8116773905095511, 3.404334480586612, [2.02013605, 3.08825397]], 
            [5.467519199250946, 1, 1, 0, 4.715271845742089, 5.228908728929915, [4.94585034]], 
            [5.467519199250946, 1, 1, 0, 5.760169805742089, 6.273806688929915, [5.9907483]]
        ],
        [   
            [5.692749210796667, 1, 2, 0, 0.5505002145766312, 2.1504077408314988, [0.7662585, 1.81115646]], 
            [5.467519199250946, 1, 1, 0, 3.18275483574209, 3.6963917189299154, [3.41333333]], 
            [5.467519199250946, 1, 1, 0, 6.89794758574209, 7.411584468929916, [7.12852608]]
        ],
        [    
            [6.1987713701316665, 1, 2, 0, 0.2281336413563909, 1.8264886274753633, [0.41795918, 1.55573696]], 
            [5.467519199250946, 1, 1, 0, 2.62547592574209, 3.1391128089299154, [2.85605442]], 
            [5.467519199250946, 1, 1, 0, 4.483072295742089, 4.996709178929915, [4.71365079]], 
            [5.467519199250946, 1, 1, 0, 5.5279702557420896, 6.0416071389299155, [5.75854875]], 
            [5.467519199250946, 1, 1, 0, 6.57286821574209, 7.086505098929916, [6.80344671]]
        ]
    ]
)
# 6

Xa_largo = [5, 1, 1, 0, 4, 7, [5]]
Ya_largo = [5, 1, 2, 0, 2, 8, [3, 4]]
Xb_largo = [5, 1, 1, 0, 0, 3, [2]]

empty = [0, 0, 0, 0, 6, 0, []]
Xa_corto = [5, 1, 1, 0, 3, 7, [5]]
Ya_corto = [5, 1, 2, 0, 3, 8, [5, 6]]

prueba_eficacia_A = (
    [
        [
            Ya_largo # largo
        ],
        [
            Xa_largo # largo
        ]
    ]
)

prueba_eficacia_B = (
    [
        [
            Xb_largo # largo
        ],
        [
            empty # largo
        ]
    ]
)
import os


def createScene(rootNode):
    rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.AnimationLoop',
        'Sofa.Component.Constraint.Lagrangian.Correction','Sofa.Component.Constraint.Lagrangian.Solver',
        'Sofa.Component.Engine.Select','Sofa.Component.IO.Mesh','Sofa.Component.LinearSolver.Direct','Sofa.Component.Mapping.Linear',
        'Sofa.Component.Mass','Sofa.Component.ODESolver.Backward','Sofa.Component.SolidMechanics.FEM.Elastic',
        'Sofa.Component.SolidMechanics.Spring','Sofa.Component.StateContainer','Sofa.Component.Topology.Container.Constant',
        'Sofa.Component.Visual','Sofa.GL.Component.Rendering3D', 'Sofa.GUI.Component'])

    rootNode.addObject('VisualStyle',
                       displayFlags='showVisualModels showBehaviorModels showCollisionModels '
                                    'hideBoundingCollisionModels hideForceFields '
                                    'showInteractionForceFields hideWireframe')
    rootNode.addObject('AttachBodyButtonSetting',stiffness=1)

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('BlockGaussSeidelConstraintSolver', maxIterations=1000, tolerance=0.001)

    ##########################################
    # FEM Model                              #
    ##########################################
    model = rootNode.addChild('model')
    model.addObject('EulerImplicitSolver', rayleighStiffness=0.2, rayleighMass=0.2)  ##--> Our integration scheme
    model.addObject('SparseLDLSolver')                                               ##--> Linear solver used to inverse A

    model.addObject('MeshVTKLoader', name='loader', filename='../PneuNets_remeshed.vtk')         ##--> Load our topology
    model.addObject('MeshTopology', src='@loader', name='container')

    model.addObject('MechanicalObject')                                              ##--> Contain all problem vectors
    model.addObject('UniformMass', totalMass=0.5)                                    ##--> Define the mass
    model.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3,   
                    youngModulus=100)                                                ##--> Define the constitutive law

    
    model.addObject('LinearSolverConstraintCorrection')                              ##--> Define the way the Schur complement is computed



    ##########################################
    # Visualization                          #
    ##########################################
    modelVisu = model.addChild('visu')                                               ##--> Add visualization
    modelVisu.addObject('MeshSTLLoader', filename="../PneuNets.stl", name="loader")
    modelVisu.addObject('OglModel', src=modelVisu.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6])
    modelVisu.addObject('BarycentricMapping')

    return rootNode

import os


def createScene(rootNode):
    rootNode.addObject('RequiredPlugin', pluginName=['SoftRobots','SoftRobots.Inverse','Sofa.Component.AnimationLoop',
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
    model.addObject('EulerImplicitSolver', rayleighStiffness=0.2, rayleighMass=0.2)
    model.addObject('SparseLDLSolver')

    model.addObject('MeshVTKLoader', name='loader', filename='../PneuNets_remeshed.vtk')
    model.addObject('MeshTopology', src='@loader', name='container')

    model.addObject('MechanicalObject')
    model.addObject('UniformMass', totalMass=0.5)
    model.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3,
                    youngModulus=100)

    model.addObject('BoxROI', name='boxROI', box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
                    position=model.MechanicalObject.position.linkpath,
                    tetrahedra=model.container.tetrahedra.linkpath)
    model.addObject('RestShapeSpringsForceField', points=model.boxROI.indices.linkpath, stiffness=1e12)
    model.addObject('LinearSolverConstraintCorrection')



    ##########################################
    # Pressure Actuator                      #
    ##########################################
    cavity = model.addChild('cavity')
    cavity.addObject('MeshSTLLoader', name='loader', filename='../PneuNets_Cavity.stl') ##--> Load the surface mesh on which the pressure will be applied
    cavity.addObject('MeshTopology', src=cavity.loader.linkpath, name='topo')
    cavity.addObject('MechanicalObject', name='cavity')
    cavity.addObject('SurfacePressureConstraint', name='SPC',template='Vec3', triangles=cavity.topo.triangles.linkpath,
                     maxVolumeGrowthVariation=500, minPressure=0)                    ##--> This is the pressure constraint
    cavity.addObject('BarycentricMapping')                                           ##--> Mapped on the real object


    ##########################################
    # Visualization                          #
    ##########################################
    modelVisu = model.addChild('visu')
    modelVisu.addObject('MeshSTLLoader', filename="../PneuNets.stl", name="loader")
    modelVisu.addObject('OglModel', src=modelVisu.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6])
    modelVisu.addObject('BarycentricMapping')

    return rootNode


import Sofa

uparrow = chr(19)
downarrow = chr(21)


class ControlConstantForce(Sofa.Core.Controller):

    def __init__(self, *args, **kwargs):
        # These are needed (and the normal way to override from a python class)
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        self.CFF = kwargs.get("ForceField")

    def onKeypressedEvent(self, event):
        key = event["key"]

        if key==uparrow :
            with self.CFF.totalForce.writeableArray() as wa:
                wa[1] += 4.

        if key==downarrow :
            with self.CFF.totalForce.writeableArray() as wa:
                wa[1] -= 4.


def createScene(rootNode):

	rootNode.name = "RootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject("DefaultAnimationLoop", name="animation_loop", computeBoundingBox=False)
	
	rootNode.addObject("RequiredPlugin", pluginName=["Sofa.Component.StateContainer","Sofa.Component.Mass","Sofa.Component.MechanicalLoad",
												     "Sofa.Component.LinearSolver.Iterative","Sofa.Component.ODESolver.Backward",
													 "Sofa.Component.IO.Mesh","Sofa.Component.Topology.Container.Dynamic",
													 "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.Topology.Container.Constant",
													 "Sofa.Component.Visual","Sofa.Component.Mapping.Linear","Sofa.GL.Component.Rendering3D",
													 "Sofa.Component.Constraint.Projective","Sofa.Component.Engine.Select", "Sofa.GUI.Component"])

	rootNode.addObject("MeshVTKLoader", name="mesh_loader_coarse", filename="../PneuNets_remeshed.vtk")
	rootNode.addObject("AttachBodyButtonSetting", name="mouse_config", stiffness=1)
	rootNode.addObject("VisualStyle", name="visual_options", displayFlags="showForceFields showBehaviorModels")
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver", name="integration_scheme")
	mechanicalModel.addObject("CGLinearSolver", name="iterative_linear_solver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	mechanicalModel.addObject("MeshTopology", name="topology_container", src="@../mesh_loader_coarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="state_container", showObject=True)
	
	mechanicalModel.addObject("TetrahedronFEMForceField", name="elastic_material_law", template="Vec3", poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject("MeshMatrixMass", name="mass", template="Vec3,Vec3", totalMass=0.5)
	
	mechanicalModel.addObject("BoxROI", name="box_ROI", box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
						      position=mechanicalModel.state_container.position.linkpath,
							  tetrahedra=mechanicalModel.topology_container.tetrahedra.linkpath)
	mechanicalModel.addObject("FixedProjectiveConstraint", name="fixed_boundary", indices=mechanicalModel.box_ROI.indices.linkpath)

	mechanicalModel.addObject("SphereROI", name="select_nodes_pulled_down", centers=[[-200, 15, 0]], radii=[5], drawROI=False, drawPoints=True, drawSize=10)
	CFF = mechanicalModel.addObject("ConstantForceField", name="force_tip_node", totalForce=[0, 0, 0], indices=mechanicalModel.select_nodes_pulled_down.indices.linkpath, showArrowSize=5) # Project constraint enforcing fixed DoFs
	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject("MeshSTLLoader", name="mesh_loader_surface", filename="../PneuNets_remeshed.stl")
	visualModel.addObject("OglModel", name="visual_model", src=visualModel.mesh_loader_surface.linkpath, color=[0.7, 0.7, 0.7, 0.6])
	visualModel.addObject("BarycentricMapping", name="visual_mapping", input="@../state_container", output="@visual_model")
	
	mechanicalModel.addObject( ControlConstantForce(name="ControlConstantForce", ForceField=CFF) )

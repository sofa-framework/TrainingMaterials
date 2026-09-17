import Sofa
from Sofa.Units.Definitions import s, m, mm, N, mN, kg, kPa  
from Sofa.Units.UnitSystem import MechanicalUnitSystem
from math import pi, sin

scene_unit = MechanicalUnitSystem(s, mm, kg)

uparrow = chr(19)
downarrow = chr(21)


class AddingParticles(Sofa.Core.Controller):

	def __init__(self, *args, **kwargs):
		# These are needed (and the normal way to override from a python class)
		Sofa.Core.Controller.__init__(self, *args, **kwargs)
		self.rootNode = kwargs.get("rootNode")
		self.iteration = 0

	def generateRadius(self):
		return 2.5*sin(self.iteration/5.5*pi - pi/4) + 5
	
	def generatXPos(self):
		return self.iteration%11 * 10  -120

	def updateCollisionPipeline(self):
		self.rootNode.removeObject(self.rootNode.collision_pipeline)
		self.rootNode.addObject("CollisionPipeline", name="collision_pipeline")
		self.rootNode.collision_pipeline.init()

	def addFallingParticle(self, node):
		iteration_loc = self.iteration
		newParticle = node.addChild("ParticleToCollideWith-"+str(iteration_loc))
		newParticle.addObject("EulerImplicitSolver")
		newParticle.addObject("SparseLDLSolver", name="linear_solver", template="CompressedRowSparseMatrixMat3x3d")
		newParticle.addObject("MechanicalObject", template="Rigid3", name="myParticle", position=[self.generatXPos(), 50, 0,  0,0,0,1], showObject=True)
		newParticle.addObject("UniformMass", totalMass=0.002)
		newParticle.addObject("ConstantForceField", totalForce=[0,4.5,0,0,0,0], indices=0)
		newParticle.addObject("SphereCollisionModel", radius=self.generateRadius(), contactStiffness=50)
		newParticle.init()
		self.iteration = iteration_loc +1
		self.updateCollisionPipeline()
    
	def removeFallingParticle(self, node):
		iteration_loc = self.iteration - 1
		if iteration_loc >= 0:
			name = "ParticleToCollideWith-"+str(iteration_loc)
			nodeToDelete = self.rootNode.getChild(str(name))
			for obj in nodeToDelete.objects:
				nodeToDelete.removeObject(obj)

			myParticleNode = self.rootNode.removeChild(str(name))
			self.iteration = iteration_loc
			self.updateCollisionPipeline()
    
	def onKeypressedEvent(self, event):
		key = event["key"]

		if key==uparrow :
			self.addFallingParticle(self.rootNode)
        
		if key==downarrow :
			self.removeFallingParticle(self.rootNode)


def createScene(rootNode):

	rootNode.name = "RootNode"
	rootNode.dt = scene_unit(0.01, s)
	rootNode.gravity = [0, scene_unit(-9.81, N/kg), 0]

	rootNode.addObject("DefaultAnimationLoop", name="animation_loop", computeBoundingBox=False)
	
	rootNode.addObject("RequiredPlugin", pluginName=["Sofa.Component.StateContainer","Sofa.Component.Mass","Sofa.Component.MechanicalLoad",
												     "Sofa.Component.LinearSolver.Direct","Sofa.Component.ODESolver.Backward",
													 "Sofa.Component.IO.Mesh","Sofa.Component.Topology.Container.Dynamic",
													 "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.Topology.Container.Constant",
													 "Sofa.Component.Visual","Sofa.Component.Mapping.Linear","Sofa.GL.Component.Rendering3D",
													 "Sofa.Component.Constraint.Projective","Sofa.Component.Engine.Select","Sofa.Component.Collision.Geometry",
													 "Sofa.Component.Collision.Detection.Intersection","Sofa.Component.Collision.Detection.Algorithm",
													 "Sofa.Component.Collision.Response.Contact", "Sofa.GUI.Component"])

	rootNode.addObject("VisualStyle", name="visual_options", displayFlags="showForceFields showCollisionModels showBehaviorModels showDetectionOutputs")

	rootNode.addObject("MeshVTKLoader", name="mesh_loader_coarse", filename="../PneuNets_remeshed.vtk")

	rootNode.addObject("AttachBodyButtonSetting", name="mouse_config", stiffness=1)
	
    ##########################################
    # Collision pipeline definition : broad phase / narrow phase / response
	rootNode.addObject("CollisionPipeline", name="collision_pipeline")
	rootNode.addObject("BruteForceBroadPhase", name="broad_phase") # Broad phase
	rootNode.addObject("BVHNarrowPhase", name="narrow_phase") # Narrow phase
	rootNode.addObject("MinProximityIntersection", name="narrow_phase_intersection", alarmDistance="4", contactDistance="0.5") # Intersection method used for the narrow phase
	rootNode.addObject("CollisionResponse", name="collision_response", response="PenalityContactForceField") # Reponse method when a contact is detected in the narrow phase
	##########################################
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver", name="integration_scheme")
	mechanicalModel.addObject("SparseLDLSolver", name="linear_solver", template="CompressedRowSparseMatrixMat3x3d")
	
	mechanicalModel.addObject("MeshTopology", name="topology_container", src="@../mesh_loader_coarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="state_container", showObject=True)
	
	mechanicalModel.addObject("TetrahedronFEMForceField", name="elastic_material_law", template="Vec3", poissonRatio=0.3, youngModulus=scene_unit(800, kPa))
	mechanicalModel.addObject("MeshMatrixMass", name="mass", template="Vec3,Vec3", massDensity=scene_unit(1e3, kg/m**3))
	
	mechanicalModel.addObject("BoxROI", name="box_ROI", box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
						      position=mechanicalModel.state_container.position.linkpath,
							  tetrahedra=mechanicalModel.topology_container.tetrahedra.linkpath)
	mechanicalModel.addObject("FixedProjectiveConstraint", name="fixed_boundary", indices=mechanicalModel.box_ROI.indices.linkpath)

	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject("MeshSTLLoader", name="mesh_loader_surface", filename="../PneuNets_remeshed.stl")
	visualModel.addObject("OglModel", name="visual_model", src=visualModel.mesh_loader_surface.linkpath, color=[0.7, 0.7, 0.7, 1])
	visualModel.addObject("BarycentricMapping", name="visual_mapping", input="@../state_container", output="@visual_model")
	
	##########################################
	# Collision representation of the finger object
	collisionlModel = mechanicalModel.addChild("Collision")
	collisionlModel.addObject("MeshTopology", name="topology_container", src=visualModel.mesh_loader_surface.linkpath) # Use the same mesh topology than the visual model
	collisionlModel.addObject("MechanicalObject", name="storing_forces") # Mechanical object storing the DoFs corresponding to the contact points and associated forces
	collisionlModel.addObject("TriangleCollisionModel", name="triangle_collision_model", contactStiffness=3) # Triangular primitives used at the narrow phase
	collisionlModel.addObject("BarycentricMapping", name="collision_mapping", input="@../state_container", output="@storing_forces") # Barycentric mapping connecting the two representations with different topologies

	rootNode.addObject( AddingParticles(name="AddingParticles", rootNode=rootNode) )


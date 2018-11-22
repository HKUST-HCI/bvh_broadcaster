import tf
import math
import numpy
import rospy
import string
import argparse

# Node
class Node:
    def __init__(self, root=False):
        self.name = None
        self.channels = []
        self.offset = (0,0,0)
        self.children = []
        self._is_root = root

    def isRoot(self):
        return self._is_root

    def isEndSite(self):
        return len(self.children)==0
    

# BVHReader
class BVHReader:
    def __init__(self, filename):

        self.filename = filename
        # A list of unprocessed tokens (strings)
        self.tokenlist = []
        # The current line number
        self.linenr = 0

        # Root node
        self._root = None
        self._nodestack = []

        # Total number of channels
        self._numchannels = 0

    def onHierarchy(self, root):
        pass

    def onMotion(self, frames, dt):
        pass

    def onFrame(self, values):
        pass

    # read
    def read(self):
        """Read the entire file.
        """
        self.fhandle = file(self.filename)

        self.readHierarchy()
        self.onHierarchy(self._root)
        self.readMotion()

    # readMotion
    def readMotion(self):
        """Read the motion samples.
        """
        # No more tokens (i.e. end of file)? Then just return 
        try:
            tok = self.token()
        except StopIteration:
            return
        
        if tok!="MOTION":
            raise SyntaxError("Syntax error in line %d: 'MOTION' expected, got '%s' instead"%(self.linenr, tok))

        # Read the number of frames
        tok = self.token()
        if tok!="Frames:":
            raise SyntaxError("Syntax error in line %d: 'Frames:' expected, got '%s' instead"%(self.linenr, tok))

        frames = self.intToken()

        # Read the frame time
        tok = self.token()
        if tok!="Frame":
            raise SyntaxError("Syntax error in line %d: 'Frame Time:' expected, got '%s' instead"%(self.linenr, tok))
        tok = self.token()
        if tok!="Time:":
            raise SyntaxError("Syntax error in line %d: 'Frame Time:' expected, got 'Frame %s' instead"%(self.linenr, tok))

        dt = self.floatToken()

        self.onMotion(frames, dt)

        # Read the channel values
        for i in range(frames):
            s = self.readLine()
            a = s.split()
            if len(a)!=self._numchannels:
                raise SyntaxError("Syntax error in line %d: %d float values expected, got %d instead"%(self.linenr, self._numchannels, len(a)))
            values = map(lambda x: float(x), a)
            self.onFrame(values)


    # readHierarchy
    def readHierarchy(self):
        """Read the skeleton hierarchy.
        """
        tok = self.token()
        if tok!="HIERARCHY":
            raise SyntaxError("Syntax error in line %d: 'HIERARCHY' expected, got '%s' instead"%(self.linenr, tok))

        tok = self.token()
        if tok!="ROOT":
            raise SyntaxError("Syntax error in line %d: 'ROOT' expected, got '%s' instead"%(self.linenr, tok))

        self._root = Node(root=True)
        self._nodestack.append(self._root)
        self.readNode()

    # readNode
    def readNode(self):
        """Read the data for a node.
        """

        # Read the node name (or the word 'Site' if it was a 'End Site'
        # node)
        name = self.token()
        self._nodestack[-1].name = name
        
        tok = self.token()
        if tok!="{":
            raise SyntaxError("Syntax error in line %d: '{' expected, got '%s' instead"%(self.linenr, tok))

        while 1:
            tok = self.token()
            if tok=="OFFSET":
                x = self.floatToken()
                y = self.floatToken()
                z = self.floatToken()
                self._nodestack[-1].offset = (x,y,z)
            elif tok=="CHANNELS":
                n = self.intToken()
                channels = []
                for i in range(n):
                    tok = self.token()
                    if tok not in ["Xposition", "Yposition", "Zposition",
                                  "Xrotation", "Yrotation", "Zrotation"]:
                        raise SyntaxError("Syntax error in line %d: Invalid channel name: '%s'"%(self.linenr, tok))                        
                    channels.append(tok)
                self._numchannels += len(channels)
                self._nodestack[-1].channels = channels
            elif tok=="JOINT":
                node = Node()
                self._nodestack[-1].children.append(node)
                self._nodestack.append(node)
                self.readNode()
            elif tok=="End":
                node = Node()
                self._nodestack[-1].children.append(node)
                self._nodestack.append(node)
                self.readNode()
            elif tok=="}":
                if self._nodestack[-1].isEndSite():
                    self._nodestack[-1].name = "End Site"
                self._nodestack.pop()
                break
            else:
                raise SyntaxError("Syntax error in line %d: Unknown keyword '%s'"%(self.linenr, tok))
        

    # intToken
    def intToken(self):
        """Return the next token which must be an int.
        """

        tok = self.token()
        try:
            return int(tok)
        except ValueError:
            raise SyntaxError("Syntax error in line %d: Integer expected, got '%s' instead"%(self.linenr, tok))

    # floatToken
    def floatToken(self):
        """Return the next token which must be a float.
        """

        tok = self.token()
        try:
            return float(tok)
        except ValueError:
            raise SyntaxError("Syntax error in line %d: Float expected, got '%s' instead"%(self.linenr, tok))

    # token
    def token(self):
        """Return the next token."""

        # Are there still some tokens left? then just return the next one
        if self.tokenlist!=[]:
            tok = self.tokenlist[0]
            self.tokenlist = self.tokenlist[1:]
            return tok

        # Read a new line
        s = self.readLine()
        self.createTokens(s)
        return self.token()

    # readLine
    def readLine(self):
        """Return the next line.

        Empty lines are skipped. If the end of the file has been
        reached, a StopIteration exception is thrown.  The return
        value is the next line containing data (this will never be an
        empty string).
        """
        # Discard any remaining tokens
        self.tokenlist = []
      
        # Read the next line
        while 1:
            s = self.fhandle.readline()
            self.linenr += 1
            if s=="":
                raise StopIteration
            return s

    # createTokens
    def createTokens(self, s):
        """Populate the token list from the content of s.
        """
        s = s.strip()
        a = s.split()
        self.tokenlist = a

class BVHBroadcaster(BVHReader):
    def __init__(self, filename, root_frame):
        BVHReader.__init__(self, filename)
        self.br = tf.TransformBroadcaster()
        self.all_motions = []
        self.dt = 1
        self.num_motions = 1
        self.root_frame = root_frame

        self.counter = 0
        self.this_motion = None

        self.scaling_factor = 0.1

    def onHierarchy(self, root):
        self.scaling_factor = 0.1/root.children[0].children[0].offset[0]

    def onMotion(self, frames, dt):
        self.dt = dt
        self.num_motions = frames

    def onFrame(self, values):
        self.all_motions.append(values)

    def broadcastRootJoint(self, root, parent_frame):
        if root.isEndSite():
            return

        num_channels = len(root.channels)

        flag_trans = 0
        flag_rot = 0

        mat_rot = numpy.array([ [1.,0.,0.,0.], 
                                [0.,1.,0.,0.], 
                                [0.,0.,1.,0.], 
                                [0.,0.,0.,1.] ])

        for channel in root.channels:
            keyval = self.this_motion[self.counter]
            if(channel == "Xposition"):
                flag_trans = True
                x = keyval
            elif(channel == "Yposition"):
                flag_trans = True
                y = keyval
            elif(channel == "Zposition"):
                flag_trans = True
                z = keyval
            elif(channel == "Xrotation"):
                flag_rot = True
                xrot = keyval
                theta = math.radians(xrot)
                c = math.cos(theta)
                s = math.sin(theta)
                mat_x_rot = numpy.array([ [1.,0.,0.,0.], 
                                          [0., c,-s,0.], 
                                          [0., s, c,0.], 
                                          [0.,0.,0.,1.] ])
                mat_rot = numpy.matmul(mat_rot, mat_x_rot)

            elif(channel == "Yrotation"):
                flag_rot = True
                yrot = keyval
                theta = math.radians(yrot)
                c = math.cos(theta)
                s = math.sin(theta)
                mat_y_rot = numpy.array([ [ c,0., s,0.],
                                          [0.,1.,0.,0.],
                                          [-s,0., c,0.],
                                          [0.,0.,0.,1.] ])
                mat_rot = numpy.matmul(mat_rot, mat_y_rot)

            elif(channel == "Zrotation"):
                flag_rot = True
                zrot = keyval
                theta = math.radians(zrot)
                c = math.cos(theta)
                s = math.sin(theta)
                mat_z_rot = numpy.array([ [ c,-s,0.,0.],
                                          [ s, c,0.,0.],
                                          [0.,0.,1.,0.],
                                          [0.,0.,0.,1.] ])
                mat_rot = numpy.matmul(mat_rot, mat_z_rot)
            else:
                return
            self.counter += 1
        
        if flag_trans:
            temp_trans = (self.scaling_factor * (x + root.offset[0]), 
                          self.scaling_factor * (y + root.offset[1]), 
                          self.scaling_factor * (z + root.offset[2]))
        else:
            temp_trans = (self.scaling_factor * (root.offset[0]), 
                          self.scaling_factor * (root.offset[1]), 
                          self.scaling_factor * (root.offset[2]))

        if root.isRoot():
            theta = math.radians(90)
            c = math.cos(theta)
            s = math.sin(theta)
            mat_x_rot = numpy.array([ [1.,0.,0.],
                                      [0., c,-s],
                                      [0., s, c]])
            mat_z_rot = numpy.array([ [ c,-s,0.,0.],
                                      [ s, c,0.,0.],
                                      [0.,0.,1.,0.],
                                      [0.,0.,0.,1.] ])
            temp_trans = numpy.matmul(mat_x_rot, temp_trans)
            mat_rot = numpy.matmul(mat_rot, mat_z_rot)

        temp_rot = tf.transformations.quaternion_from_matrix(mat_rot)

        self.br.sendTransform(temp_trans, temp_rot, rospy.Time.now(), root.name, parent_frame)

        for each_child in root.children:
            self.broadcastRootJoint(each_child, root.name)

    def broadcast(self, loop=False):
        self.read()
        rate = rospy.Rate(1/self.dt)

        while not rospy.is_shutdown():
            for ind in range(self.num_motions):
                self.counter = 0
                self.this_motion = self.all_motions[ind]

                self.broadcastRootJoint(self._root, self.root_frame)
                if rospy.is_shutdown():
                    break
                rate.sleep()
            if not loop:
                break

def argsparser():
    parser = argparse.ArgumentParser("python BVHBroadcaster.py")
    parser.add_argument('bvh_file', help="A path to bvh file that you want to broadcast")
    parser.add_argument('base_frame', help="An existing frame in rviz on which the skeleton will be loaded")
    parser.add_argument('-n', '--name', help="Node name, default: BVHBroadcaster", default="BVHBroadcaster")
    parser.add_argument('-l', '--loop', help="Loop broadcasting", action="store_true")
    return parser.parse_args()

def main(args):
    rospy.init_node(args.name)
    # file_name = "/home/mingfei/Documents/RobotManipulationProject/mocap/62/62_07.bvh"
    bvh_test = BVHBroadcaster(args.bvh_file, args.base_frame)
    rospy.loginfo("Broadcasting bvh file (%s) on frame %s"%(args.bvh_file, args.base_frame))
    if args.loop:
        rospy.loginfo("Loop")
    else: 
        rospy.loginfo("Only once")
    bvh_test.broadcast(loop=args.loop)
    rospy.loginfo("Broadcasting done")

def test():
    rospy.init_node("BVHBroadcaster")
    file_name = "/home/mingfei/Documents/projects/RobotManipulationProject/mocap/62/62_07.bvh"
    bvh_test = BVHBroadcaster(file_name, "world")
    bvh_test.broadcast(loop=True)

if __name__ == "__main__":
    args = argsparser()
    main(args)
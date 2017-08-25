#!/usr/bin/env python
# $Id: checkxAOD.py 690078 2015-08-19 08:03:39Z krasznaa $
#
# This is a standalone implementation of the xAOD checking script. It just needs
# a functional ROOT installation to work.
#
# @author Attila Krasznahorkay <Attila.Krasznahorkay@cern.ch>
#
# $Revision: 690078 $
# $Date: 2015-08-19 10:03:39 +0200 (Wed, 19 Aug 2015) $
#

## C(++) style main function
#
# I just prefer writing executable Python code like this...
#
# @returns 0 on success, something else on failure
#
def main():

    # Set up the command line option parser:
    from optparse import OptionParser
    parser = OptionParser( usage = "usage: %prog [-f] xAOD.pool.root" )
    parser.add_option( "-f", "--file",
                       dest = "fileName",
                       help = "The path to the xAOD file to analyse" )
    ( options, args ) = parser.parse_args()

    # Get the file name(s), taking all options into account:
    fileNames = []
    if len( args ) > 0:
        fileNames = [ arg for arg in args if arg[ 0 ] != "-" ]
        pass
    if ( options.fileName == None ) and ( len( fileNames ) == 0 ):
        parser.print_help()
        return 1
    if options.fileName != None:
        fileNames.append(
            os.path.expandvars( os.path.expanduser( options.fileName ) ) )
        pass
    fileNames = set( fileNames )

    # Set up ROOT:
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError

    # Loop over the files:
    for fileName in fileNames:
        # Print their contents using the helper function:
        printFileInfo( fileName )
        pass
    
    # Return gracefully:
    return 0

## Class for holding information about a single container
#
# Modeled on PoolRecord from the offline code...
#
class ContainerInfo( object ):
    ## Constructor
    def __init__( self, name, memSize, diskSize, nEntries ):
        # Call the base class's constructor:
        object.__init__( self )
        # Remember the properties:
        self._name     = name
        self._memSize  = memSize
        self._diskSize = diskSize
        self._nEntries = nEntries
        return
    ## The name of the container
    def name( self ):
        return self._name
    ## Size of the container in memory in kilobytes
    def memSize( self ):
        return float( self._memSize ) / 1024.
    ## Size of the container on disk in kilobytes
    def diskSize( self ):
        return float( self._diskSize ) / 1024.
    ## Average size of the container per event in kilobytes
    def diskSizePerEntry( self ):
        return self.diskSize() / self._nEntries
    ## Compression factor for the container
    def compression( self ):
        return self.memSize() / self.diskSize()
    ## The number of entries saved for this container
    def nEntries( self ):
        return self._nEntries

## Function printing information about a single xAOD file
#
# This function is used to print the contents of a given xAOD file.
#
# @param fileName The name of the file to print information about
#
def printFileInfo( fileName ):

    # Open the file:
    import ROOT
    f = ROOT.TFile.Open( fileName, "READ" )
    if not f or f.IsZombie():
        raise "Couldn't open file %s" % fileName

    # Get the main event tree from the file:
    t = f.Get( "CollectionTree" )
    if not t:
        raise "Couldn't find 'CollectionTree; in file %s" % fileName

    # The collected data:
    infoForCont = {}

    # The entries in the TTree, for cross-checking:
    entries = t.GetEntries()

    # Get all the branches of the file:
    branches = t.GetListOfBranches()
    for i in xrange( branches.GetEntries() ):
        # Get the branch:
        branch = branches.At( i )
        # A little security check:
        if branch.GetEntries() != entries:
            raise "Found %i entries in branch %s instead of %i" % \
              ( branch.GetEntries(), branch.GetName(), entries )
        # "Decode" the name of the branch:
        brName = branch.GetName()
        import re
        # Check if this is a static auxiliary branch:
        m = re.match( "(.*)Aux\..*", branch.GetName() )
        if m:
            brName = m.group( 1 )
            pass
        # Check if this is a dynamic auxiliary branch:
        m = re.match( "(.*)AuxDyn\..*", branch.GetName() )
        if m:
            brName = m.group( 1 )
            pass
        # Get the information that we need:
        if brName in infoForCont.keys():
            infoForCont[ brName ]._memSize  += branch.GetTotBytes( "*" )
            infoForCont[ brName ]._diskSize += branch.GetZipBytes( "*" )
        else:
            infoForCont[ brName ] = ContainerInfo( brName,
                                                   branch.GetTotBytes( "*" ),
                                                   branch.GetZipBytes( "*" ),
                                                   entries )
            pass
        pass

    # Sort the collected info based on the on-disk size of the containers:
    orderedData = []
    for cName in infoForCont.keys():
        orderedData += [ infoForCont[ cName ] ]
        pass
    import operator
    orderedData.sort( key = operator.attrgetter( "_diskSize" ) )

    # Finally, print the collected information:
    print( "=" * 120 )
    print( " File: %s" % fileName )
    print( "-" * 120 )
    print( "    Memory size        Disk Size       Size/Event  Compression "
           "Entries  Name (Type)" )
    print( "-" * 120 )
    for d in orderedData:
        # Try to get the type of the object/container:
        intBr = t.GetBranch( d.name() )
        className = "<!!!Interface missing!!!>"
        if intBr:
            className = intBr.GetClassName()
            pass
        # The name and type of the branch in question:
        nameType = "%s (%s)" % ( d.name(), className )
        print( " %12.2f kB  %12.2f kB  %7.2f kB/event   %5.2f  %8i   %s" % \
               ( d.memSize(), d.diskSize(),
                 d.diskSizePerEntry(),
                 d.compression(),
                 d.nEntries(), nameType ) )
    print( "=" * 120 )
    return

# Run the main function in "normal mode":
if __name__ == "__main__":
    import sys
    sys.exit( main() )

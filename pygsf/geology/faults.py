# -*- coding: utf-8 -*-


from .defaults import *
from .exceptions import *
from ..orientations.orientations import *


class Slick(object):
    """
    Slickeline.
    It can be represented by a Direct instance, when it has a movement sense,
    or by an Axis instance, when the movement sense is unknown or not sure.
    When the movement sense is known, the instance indicates the displacement of the block that is:
    - for a horizontal or a dipping, non vertical fault: the upper block
    - for a vertical fault: the block individuated by the (formal) dip direction.
    """

    def __init__(self, trend: [int, float], plunge: [int, float], known: bool=True):
        """"
        Class constructors from trend, plunge and optional known movement sense flag.

        :param trend: the trend of the slickenline
        :type trend: float
        :param plunge: the slickenline plunge
        :type plunge: float
        :param known: the known movement sense flag
        :type known: bool
        :return: the Slick instance

        Example:
          >>> Slick(90, 10)
          Slick(az: 90.00°, pl: 10.00°, known_dir: True)
          >>> Slick(90, 10, known=False)
          Slick(az: 90.00°, pl: 10.00°, known_dir: False)
          >>> Slick("90", 10, False)
          Traceback (most recent call last):
          ...
          pygsf.geology.exceptions.SlickInputTypeException: Trend must be a number
        """

        if not isinstance(trend, (int, float)):
            raise SlickInputTypeException("Trend must be a number")
        if not isinstance(plunge, (int, float)):
            raise SlickInputTypeException("Plunge must be a number")
        if not isinstance(known, bool):
            raise SlickInputTypeException("Known movement sense must be a boolean")

        if known:
            self.s = Direct.fromAzPl(trend, plunge)
        else:
            self.s = Axis.fromAzPl(trend, plunge)

    def __repr__(self):

        return "Slick(az: {:.2f}°, pl: {:.2f}°, known_dir: {})".format(*self.s.d, self.hasKnownSense())

    @property
    def geom(self) -> [Direct, Axis]:
        """
        Returns the geometric object (Direct or Axis) defining the slickenline.

        :return: Direct or Axis instance

        Examples:
          >>> Slick(90, 45).geom
          Direct(az: 90.00°, pl: 45.00°)
          >>> Slick(90, 45, False).geom
          Axis(az: 90.00°, pl: 45.00°)
        """

        return self.s

    def hasKnownSense(self) -> bool:
        """
        Check whether the slickenline has known movement sense.

        Example:
          >>> Slick(90, 45).hasKnownSense()
          True
          >>> Slick(90, 45, False).hasKnownSense()
          False
        """

        return not isinstance(self.s, Axis)

    def hasUnknownSense(self) -> bool:
        """
        Check whether the slickenline has unknown/uncertain movement sense.

        Example:
          >>> Slick(90, 45, False).hasUnknownSense()
          True
          >>> Slick(90, 45).hasUnknownSense()
          False
        """

        return not self.hasKnownSense()

    def setKnownSense(self) -> 'Slick':
        """
        Return a new slickenline with movement sense set to known.

        Example:
          >>> Slick(180, -30, False).setKnownSense()
          Slick(az: 180.00°, pl: -30.00°, known_dir: True)
        """

        return Slick(*self.s.d, True)

    def setUnknownSense(self) -> 'Slick':
        """
        Set to unknown/uncertain the movement sense for the current Slickline instance.

        Example:
          >>> Slick(180, -30).setUnknownSense()
          Slick(az: 180.00°, pl: -30.00°, known_dir: False)
        """

        return Slick(*self.s.d, False)

    def invert(self) -> Optional['Slick']:
        """
        Invert the slickenline sense, when known, otherwise raise SlickSenseException.

        Example:
         >>> Slick(30, 45, False).invert()
         Slick(az: 210.00°, pl: -45.00°, known_dir: False)
         >>> Slick(30, 45).invert()
         Slick(az: 210.00°, pl: -45.00°, known_dir: True)
        """

        return Slick(*self.s.opposite().d, self.hasKnownSense())


class Fault(object):
    """
    Represent a fault plane, composed by a Plane instance, and zero, one or more slickenlines,
    stored by a list of Slick instances (None when no slickenlines).
    """

    def __init__(self, azim: [int, float], dip_ang: [int, float],
       is_rhr_strike: bool=False, slickenlines: Sequence[Slick]=None):
        """
        Create an instance of a Fault.

        :param  azim:  azimuth of the plane (RHR strike or dip direction).
        :type  azim:  number or string convertible to float.
        :param  dip_ang:  Dip angle of the plane (0-90°).
        :type  dip_ang:  number or string convertible to float.
        :param is_rhr_strike: if the source azimuth is RHR strike (default is False, i.e. it is dip direction)
        :type is_rhr_strike: bool
        :param slickenlines: the slickenlines associated with the fault plane.
        :type slickenlines: list of Slick instances.
        :return: the instantiated fault instance.

        Example:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)])
          Fault(90.0, 45.0) with 1 slickeline(s)
          >>> Fault(90, 45, slickenlines=[Slick(90, 55)])
          Traceback (most recent call last):
          ...
          pygsf.geology.exceptions.FaultInputTypeException: All slickenlines must lie on the plane
        """

        if not isinstance(azim, (int, float)):
            raise FaultInputTypeException("Azim must be a number")
        if not isinstance(dip_ang, (int, float)):
            raise FaultInputTypeException("Dip angle must be a number")

        if slickenlines is None:
            slickenlines = []

        plane = Plane(azim, dip_ang, is_rhr_strike)

        for slickenline in slickenlines:
            if not plane.contains(slickenline.s):
                raise FaultInputTypeException("All slickenlines must lie on the plane")

        self._fltpln = plane
        self._slicks = slickenlines

    def __repr__(self):

        return "Fault({}, {}) with {} slickeline(s)".format(*self.plane.dda, len(self.slicks))

    @property
    def plane(self) -> Plane:
        """
        Return fault plane, as a Plane instance.

        Example:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).plane
          Plane(090.00, +45.00)
        """

        return self._fltpln

    @property
    def numSlicks(self) -> int:
        """
        Returns the number of slickenlines.

        :return: number of slickenlines, as integer

        Examples:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).numSlicks
          1
        """

        return len(self._slicks)

    @property
    def hasSlicks(self) -> bool:
        """
        Returns the number of slickenlines.

        :return: number of slickenlines, as integer

        Examples:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).hasSlicks
          True
        """

        return self.numSlicks > 0

    @property
    def slicks(self) -> List[Slick]:
        """
        Return the slickenlines associated with the fault.
        """

        return self._slicks

    def slick(self, ndx: int=0) -> Slick:
        """
        Return the slickenline with the given index associated with the fault.

        Example:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).slick()
          Slick(az: 90.00°, pl: 45.00°, known_dir: True)
        """

        if not self._slicks:
            raise FaultInputTypeException("No slickenline defined for current Fault instance")
        elif ndx > len(self._slicks) - 1:
            raise FaultInputTypeException("Slickenline index is greater than slickenlines number")
        else:
            return self._slicks[ndx]

    def slickGeom(self, ndx: int=0) -> Optional[Direct]:
        """
        Return the geometric object (Direct or Axis) associated with slickenline.

        Example:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).slickGeom()
          Direct(az: 90.00°, pl: 45.00°)
        """

        if not self._slicks:
            raise FaultInputTypeException("No slickenline defined for current Fault instance")
        elif ndx > len(self._slicks) - 1:
            raise FaultInputTypeException("Slickenline index is greater than slickenlines number")
        else:
            return self._slicks[ndx].s

    @property
    def knownSense(self, ndx: int=0) -> bool:
        """
        Check if the Slick instance in the Fault instance has a known movement sense.

        Example:
          >>> Fault(90, 45, slickenlines=[Slick(90, 45, False)]).knownSense
          False
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).knownSense
          True
        """

        if not self._slicks:
            return None
        elif ndx > len(self._slicks) - 1:
            raise FaultInputTypeException("Slickenline index is greater than slickenlines number")
        else:
            return self._slicks[ndx].hasKnownSense()

    def rake(self, ndx: int=0) -> float:
        """
        Calculates the rake (sensu Aki & Richards, 1980) of the slickenline with the given index.
        The slickenlines must have known sense movement.

        :return: the rake value
        :rtype: float

        Examples:
          >>> Fault(180, 45, slickenlines=[Slick(90, 0)]).rake()
          0.0
          >>> Fault(180, 45, slickenlines=[Slick(0, -45)]).rake()
          90.0
          >>> Fault(180, 45, slickenlines=[Slick(270, 0)]).rake()
          180.0
          >>> Fault(180, 45, slickenlines=[Slick(180, 45)]).rake()
          -90.0
          >>> Fault(180, 45, slickenlines=[Slick(180, 45, False)]).rake()
          Traceback (most recent call last):
          ...
          pygsf.geology.exceptions.FaultInputTypeException: Slickeline must have known movement sense
          >>> Fault(90, 90, slickenlines=[Slick(0, 0)]).rake()
          0.0
          >>> Fault(90, 90, slickenlines=[Slick(90, 90)]).rake()
          -90.0
          >>> Fault(90, 90, slickenlines=[Slick(90, -90)]).rake()
          90.0
          >>> Fault(90, 90, slickenlines=[Slick(180, 1)]).rake()
          -179.0000000000001
          >>> Fault(90, 90, slickenlines=[Slick(180, -1)]).rake()
          179.0000000000001
          >>> Fault(90, 90, slickenlines=[Slick(0, 0)]).rake()
          0.0
          >>> Fault(0, 90, slickenlines=[Slick(90, 30)]).rake()
          -150.0
          >>> Fault(45, 90, slickenlines=[Slick(135, 0)]).rake()
          180.0
          >>> Fault(90, 90, slickenlines=[Slick(0, 20)]).rake()
          -19.999999999999993
          >>> Fault(90, 90, slickenlines=[Slick(180, 40)]).rake()
          -140.00000000000003
        """

        if not self.knownSense:
            raise FaultInputTypeException("Slickeline must have known movement sense")

        sl_gv = self.slickGeom(ndx)
        angle = sl_gv.angle(self.plane.rhrStrikeOrien())

        if self.plane.dipDirOrien().angle(sl_gv) < 90.0:
            return -angle
        else:
            return angle

    def isNormal(self, ndx: int=0, rk_threshold=rake_threshold, dip_angle_threshold=angle_gplane_thrshld) -> bool:
        """
        Checks if a fault has normal (downward) movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake angle
        :param dip_angle_threshold: the threshold, in degrees, for the dip angle of the geological plane
        :return: True if normal, False if not applicable

        Examples:
          >>> Fault(0, 45, slickenlines=[Slick(0, 45)]).isNormal()
          True
          >>> Fault(0, 45, slickenlines=[Slick(90, 0)]).isNormal()
          False
          >>> Fault(0, 15, slickenlines=[Slick(180, -15)]).isNormal()
          False
          >>> Fault(0, 90, slickenlines=[Slick(90, 45)]).isNormal()
          False
          >>> Fault(0, 90, slickenlines=[Slick(270, -45)]).isNormal()
          False
        """

        if self.plane.isVHighAngle(dip_angle_threshold) or self.plane.isVLowAngle(dip_angle_threshold):
            return False

        if - rk_threshold >= self.rake(ndx) >= -(180.0 - rk_threshold):
            return True
        else:
            return False

    def isReverse(self, ndx: int=0, rk_threshold=rake_threshold, dip_angle_threshold=angle_gplane_thrshld) -> bool:
        """
        Checks if a fault has reverse movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake angle
        :param dip_angle_threshold: the threshold, in degrees, for the dip angle of the geological plane
        :return: True if reverse, False if not applicable

        Examples:
          >>> Fault(90, 90, slickenlines=[Slick(0, 0)]).isReverse()
          False
          >>> Fault(90, 90, slickenlines=[Slick(90, 90)]).isReverse()
          False
          >>> Fault(90, 45, slickenlines=[Slick(0, 0)]).isReverse()
          False
          >>> Fault(90, 45, slickenlines=[Slick(270, -45)]).isReverse()
          True
          >>> Fault(90, 45, slickenlines=[Slick(90, 45)]).isReverse()
          False
        """

        if self.plane.isVHighAngle(dip_angle_threshold) or self.plane.isVLowAngle(dip_angle_threshold):
            return False

        if rk_threshold <= self.rake(ndx) <= (180.0 - rk_threshold):
            return True
        else:
            return False

    def isRightLateral(self, ndx: int=0, rk_threshold=rake_threshold, dip_angle_threshold=angle_gplane_thrshld) -> bool:
        """
        Checks if a fault has right-lateral movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake angle
        :param dip_angle_threshold: the threshold, in degrees, for the dip angle of the geological plane
        :return: True if right-lateral, False if not applicable

        Examples:
          >>> Fault(90, 90, slickenlines=[Slick(0, 0)]).isRightLateral()
          False
          >>> Fault(90, 90, slickenlines=[Slick(180, 0)]).isRightLateral()
          True
          >>> Fault(90, 45, slickenlines=[Slick(0, 0)]).isRightLateral()
          False
          >>> Fault(90, 45, slickenlines=[Slick(180, 0)]).isRightLateral()
          True
          >>> Fault(90, 45, slickenlines=[Slick(270, -45)]).isRightLateral()
          False
          >>> Fault(90, 2, slickenlines=[Slick(180, 0)]).isRightLateral()
          False
        """

        if self.plane.isVLowAngle(dip_angle_threshold):
            return False

        rake = self.rake(ndx)
        if rake >= (90.0 + rk_threshold) or rake <= (-90.0 - rk_threshold):
            return True
        else:
            return False

    def isLeftLateral(self, ndx: int=0, rk_threshold=rake_threshold, dip_angle_threshold=angle_gplane_thrshld) -> bool:
        """
        Checks if a fault has left-lateral movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake angle
        :param dip_angle_threshold: the threshold, in degrees, for the dip angle of the geological plane
        :return: True if left-lateral, False if not applicable

        Examples:
          >>> Fault(90, 90, slickenlines=[Slick(0, 0)]).isLeftLateral()
          True
          >>> Fault(90, 90, slickenlines=[Slick(180, 0)]).isLeftLateral()
          False
          >>> Fault(90, 45, slickenlines=[Slick(0, 0)]).isLeftLateral()
          True
          >>> Fault(90, 45, slickenlines=[Slick(180, 0)]).isLeftLateral()
          False
          >>> Fault(90, 45, slickenlines=[Slick(270, -45)]).isLeftLateral()
          False
          >>> Fault(90, 2, slickenlines=[Slick(0, 0)]).isLeftLateral()
          False
        """

        if self.plane.isVLowAngle(dip_angle_threshold):
            return False

        if (-90.0 + rk_threshold) <= self.rake(ndx) <= (90.0 - rk_threshold):
            return True
        else:
            return False


if __name__ == "__main__":

    import doctest
    doctest.testmod()

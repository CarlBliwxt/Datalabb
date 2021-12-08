def pump(fluid, p_final, eta):
    """Adiabatically pump a fluid to pressure p_final, using
    a pump with isentropic efficiency eta."""
    h0 = fluid.h
    s0 = fluid.s
    fluid.SP = s0, p_final
    h1s = fluid.h
    isentropic_work = h1s - h0
    actual_work = isentropic_work / eta
    h1 = h0 + actual_work
    fluid.HP = h1, p_final
    return actual_work


def expand(fluid, p_final, eta):
    """Adiabatically expand a fluid to pressure p_final, using
    a turbine with isentropic efficiency eta."""
    h0 = fluid.h
    s0 = fluid.s
    fluid.SP =s0, p_final
    h1s = fluid.h
    isentropic_work = h0 - h1s
    actual_work = isentropic_work * eta
    h1 = h0 - actual_work
    fluid.HP = h1, p_final
    return actual_work

def printState(n, fluid):
    print('\n***************** State {0} ******************'.format(n))
    print(fluid.report())

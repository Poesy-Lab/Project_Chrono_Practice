# ============================================================================
# spring damper system with external force (no gravity)
# body1: spring-damper with built-in Chrono model
# body2: spring-damper with custom force functor 
# Compare the two simulations with the analytical solution (theory)
# ============================================================================


import pychrono as chrono
import pychrono.irrlicht as chronoirr
import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# Define Simulation Parameters
# 여기서 파라미터 값 조정하면서 시뮬레이션 결과가 어떻게 달라지는지 관찰
# =============================================================================

mass = 1.0

# Body1 parameters
k1 = 50
c1 = 1

# Body2 parameters
k2 = 50
c2 = 1

rest_length = 1.5

# external force (Body2)
F_amp = 10    #외력 진폭 [N]
F_freq = 10   #외력 주파수 [rad/s]

dt = 0.001
time_end = 10


# =============================================================================
# Analytical Model (Theory)
# =============================================================================

# Body1
wn1 = np.sqrt(k1/mass)
zeta1 = c1/(2*np.sqrt(k1*mass))
wd1 = wn1*np.sqrt(1-zeta1**2)

# Body2
wn2 = np.sqrt(k2/mass)
zeta2 = c2/(2*np.sqrt(k2*mass))
wd2 = wn2*np.sqrt(1-zeta2**2)


# =============================================================================
# Damping Regime Function
# =============================================================================

def damping_regime(zeta):

    if zeta < 1:
        return "Under-damped"
    elif np.isclose(zeta,1):
        return "Critical"
    else:
        return "Over-damped"


# =============================================================================
# Parameter Table Output
# =============================================================================

print("\n============================================================")
print("        Chrono Spring-Damper Validation Test")
print("============================================================")

print(f"\nMass = {mass} kg")

print("\n------------------------------------------------------------")
print(f"{'Body':<8}{'k(N/m)':<10}{'c(Ns/m)':<10}{'wn(rad/s)':<12}{'zeta':<10}{'Regime'}")
print("------------------------------------------------------------")

print(f"{'Body1':<8}{k1:<10}{c1:<10}{wn1:<12.3f}{zeta1:<10.3f}{damping_regime(zeta1)}")
print(f"{'Body2':<8}{k2:<10}{c2:<10}{wn2:<12.3f}{zeta2:<10.3f}{damping_regime(zeta2)}")

print("------------------------------------------------------------")

print("\nExternal Force (Body2)")
print("-----------------------")
print(f"Amplitude  = {F_amp} N")
print(f"Frequency  = {F_freq} rad/s")

print("============================================================\n")


# =============================================================================
# Custom Force Model (Body2)
# =============================================================================

class MySpringForce(chrono.ForceFunctor):

    def evaluate(self, time, rest_length, length, vel, link):

        Fs = -k2*(length-rest_length)
        Fd = -c2*vel
        Fext = F_amp*np.sin(F_freq*time)

        return Fs + Fd + Fext


# =============================================================================
# Create Chrono System
# =============================================================================

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0,0,0))


# =============================================================================
# Ground
# =============================================================================

ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)

ground.AddVisualShape(
    chrono.ChVisualShapeSphere(0.1),
    chrono.ChFramed(chrono.ChVector3d(-1,0,0))
)

ground.AddVisualShape(
    chrono.ChVisualShapeSphere(0.1),
    chrono.ChFramed(chrono.ChVector3d(1,0,0))
)


# =============================================================================
# Bodies
# =============================================================================

body_1 = chrono.ChBody()
body_1.SetMass(mass)
body_1.SetInertiaXX(chrono.ChVector3d(1,1,1))
body_1.SetPos(chrono.ChVector3d(-1,-3,0))
sys.AddBody(body_1)

box1 = chrono.ChVisualShapeBox(0.4,0.4,0.4)
box1.SetColor(chrono.ChColor(0.7,0,0))
body_1.AddVisualShape(box1)


body_2 = chrono.ChBody()
body_2.SetMass(mass)
body_2.SetInertiaXX(chrono.ChVector3d(1,1,1))
body_2.SetPos(chrono.ChVector3d(1,-3,0))
sys.AddBody(body_2)

box2 = chrono.ChVisualShapeBox(0.4,0.4,0.4)
box2.SetColor(chrono.ChColor(0,0,0.7))
body_2.AddVisualShape(box2)


# =============================================================================
# Springs
# =============================================================================

# Body1 → 기본 spring damper

spring_1 = chrono.ChLinkTSDA()
spring_1.Initialize(body_1, ground, True,
                    chrono.ChVector3d(0,0,0),
                    chrono.ChVector3d(-1,0,0))

spring_1.SetRestLength(rest_length)
spring_1.SetSpringCoefficient(k1)
spring_1.SetDampingCoefficient(c1)

sys.AddLink(spring_1)


# Body2 → Functor spring

force_functor = MySpringForce()

spring_2 = chrono.ChLinkTSDA()
spring_2.Initialize(body_2, ground, True,
                    chrono.ChVector3d(0,0,0),
                    chrono.ChVector3d(1,0,0))

spring_2.SetRestLength(rest_length)
spring_2.RegisterForceFunctor(force_functor)

sys.AddLink(spring_2)


# =============================================================================
# Visualization
# =============================================================================

vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)

vis.SetWindowSize(1024,768)
vis.SetWindowTitle("Chrono Spring Comparison")

vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(0,0,6))
vis.AddTypicalLights()


# =============================================================================
# Data storage
# =============================================================================

time_list=[]
disp1=[]
disp2=[]
theory=[]


# =============================================================================
# Simulation Loop
# =============================================================================

frame = 0

# equilibrium position
y_eq = -rest_length

# initial displacement
x0 = body_1.GetPos().y - y_eq


while vis.Run():

    time = sys.GetChTime()

    if time > time_end:
        print("Simulation finished")
        vis.GetDevice().closeDevice()
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)

    # simulation position
    y1 = body_1.GetPos().y
    y2 = body_2.GetPos().y

    # theory solution
    x_theory = x0 * np.exp(-zeta1*wn1*time) * np.cos(wd1*time)
    y_theory = x_theory + y_eq

    time_list.append(time)
    disp1.append(y1)
    disp2.append(y2)
    theory.append(y_theory)

    if frame % 50 == 0:
        print(
            f"{time:.3f}  "
            f"L1:{spring_1.GetLength():.3f}  "
            f"F1:{spring_1.GetForce():.3f}"
        )

    frame += 1


# =============================================================================
# Convert numpy
# =============================================================================

time=np.array(time_list)
disp1=np.array(disp1)
disp2=np.array(disp2)
theory=np.array(theory)

error1=disp1-theory
error2=disp2-theory

rmse1=np.sqrt(np.mean(error1**2))
rmse2=np.sqrt(np.mean(error2**2))

print("\nRMSE Body1 =",rmse1)
print("RMSE Body2 =",rmse2)


# =============================================================================
# Plot 1 : Body1 vs Body2
# =============================================================================

plt.figure()

plt.plot(time, disp1, color='red', label="Body1 Simulation")
plt.plot(time, disp2, color='blue', linestyle='--', label="Body2 Simulation")

plt.xlabel("Time (s)")
plt.ylabel("Displacement (m)")
plt.title("Body Displacement Comparison")

plt.legend()
plt.grid()


# =============================================================================
# Plot 2~5 : 2x2
# =============================================================================

# 전처리
fig, axs = plt.subplots(2,2, figsize=(12,8))

axs[1,0].text(0.7,0.9,f"RMSE={rmse1:.4f}", color='red',transform=axs[1,0].transAxes)
axs[1,1].text(0.7,0.9,f"RMSE={rmse2:.4f}", color='blue',transform=axs[1,1].transAxes)

# 오차 그래프 스케일 맞추기: 최대 error 저장
max_error = max(np.max(np.abs(error1)), np.max(np.abs(error2)))

# 오차 그래프 bias 추가
axs[1,0].axhline(0, color='gray', linewidth=0.9)
axs[1,1].axhline(0, color='gray', linewidth=0.9)

# ------------------------------------------------
# Body1 vs Theory
# ------------------------------------------------
axs[0,0].plot(time, disp1, color='red', label="Body1 Simulation")
axs[0,0].plot(time, theory, color='black', linestyle='--', label="Theory")

axs[0,0].set_title("Body1 Simulation vs Theory")
axs[0,0].set_xlabel("Time (s)")
axs[0,0].set_ylabel("Displacement")
axs[0,0].legend()
axs[0,0].grid()


# ------------------------------------------------
# Body2 vs Theory
# ------------------------------------------------
axs[0,1].plot(time, disp2, color='blue', label="Body2 Simulation")
axs[0,1].plot(time, theory, color='black', linestyle='--', label="Theory")

axs[0,1].set_title("Body2 Simulation vs Theory")
axs[0,1].set_xlabel("Time (s)")
axs[0,1].set_ylabel("Displacement")
axs[0,1].legend()
axs[0,1].grid()


# ------------------------------------------------
# Body1 Error
# ------------------------------------------------
axs[1,0].plot(time, error1, 
              #color='lightcoral'
              color='Black')

axs[1,0].set_title("Body1 Error (Sim - Theory)")
axs[1,0].set_xlabel("Time (s)")
axs[1,0].set_ylabel("Error (m)")
axs[1,0].set_ylim(-max_error, max_error)
axs[1,0].grid()


# ------------------------------------------------
# Body2 Error
# ------------------------------------------------
axs[1,1].plot(time, error2, 
              #color='lightskyblue'
              color='Black')

axs[1,1].set_title("Body2 Error (Sim - Theory)")
axs[1,1].set_xlabel("Time (s)")
axs[1,1].set_ylabel("Error (m)")
axs[1,1].set_ylim(-max_error, max_error)
axs[1,1].grid()


plt.tight_layout()
plt.show()

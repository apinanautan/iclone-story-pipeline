"""Select the live viewport Switch without moving the system pointer."""
import RLPy
from PySide2 import QtWidgets
app=QtWidgets.QApplication.instance()
combos=[w for w in app.allWidgets() if isinstance(w,QtWidgets.QComboBox) and w.objectName()=="qtCameraSwitchAction" and w.isVisible()]
if len(combos)!=1:raise RuntimeError("Expected one visible viewport camera selector")
combo=combos[0]
idx=combo.findText("Switch")
if idx<0:raise RuntimeError("Switch item missing")
before=combo.currentText()
if before!="Switch":combo.setCurrentIndex(idx)
app.processEvents()
RLPy.RGlobal.ForceViewportUpdate()
if combo.currentText()!="Switch":raise RuntimeError("Switch selection not verified")
print("OK native Qt viewport "+before+" -> "+combo.currentText())

import re

with open('animoon/app/src/main/java/com/example/animoon/ui/base/BaseActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

loading_methods = """
    private var loadingDialog: AlertDialog? = null

    fun showLoading(message: String) {
        if (isFinishing || isDestroyed) return
        if (loadingDialog?.isShowing == true) return

        val view = LayoutInflater.from(this).inflate(R.layout.dialog_loading, null)
        view.findViewById<android.widget.TextView>(R.id.txtLoadingMessage).text = message
        
        val builder = AlertDialog.Builder(this)
        builder.setView(view)
        builder.setCancelable(false)
        
        loadingDialog = builder.create()
        loadingDialog?.window?.setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
        loadingDialog?.show()
    }

    fun hideLoading() {
        loadingDialog?.dismiss()
        loadingDialog = null
    }
"""

if "fun showLoading" not in content:
    content = content.replace('protected open val observarSesionExpirada: Boolean = true', 'protected open val observarSesionExpirada: Boolean = true\n' + loading_methods)

with open('animoon/app/src/main/java/com/example/animoon/ui/base/BaseActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)

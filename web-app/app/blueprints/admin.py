from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
def admin():
    """
    This route is only accessible to users with the role 'admin'.
    If the current_user's role is not 'admin', a 403 error is shown.
    """
    if current_user.role != 'admin':
        abort(403)
    return render_template('admin/admin.html')

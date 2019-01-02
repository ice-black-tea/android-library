package org.ironman.framework.util;

import android.content.pm.PackageManager;
import android.content.pm.PermissionInfo;
import android.text.TextUtils;

import org.ironman.framework.AtEnvironment;

/**
 * Created by hu on 18-12-17.
 */

public class PermissionUtil {

    public enum Protection {
        dangerous,
        normal,
        signature,
        signatureOrSystem,
    }

    public static Protection getProtection(String permission) {
        try {
            return getProtection(AtEnvironment.getPackageManager().getPermissionInfo(permission, -1));
        } catch (PackageManager.NameNotFoundException e) {
            // e.printStackTrace();
        }
        return Protection.normal;
    }

    public static Protection getProtection(PermissionInfo permissionInfo) {
        switch (permissionInfo.protectionLevel & PermissionInfo.PROTECTION_MASK_BASE) {
            case PermissionInfo.PROTECTION_DANGEROUS:
                return Protection.dangerous;
            case PermissionInfo.PROTECTION_NORMAL:
                return Protection.normal;
            case PermissionInfo.PROTECTION_SIGNATURE:
                return Protection.signature;
            case PermissionInfo.PROTECTION_SIGNATURE_OR_SYSTEM:
                return Protection.signatureOrSystem;
            default:
                return Protection.normal;
        }
    }

    public static boolean isDangerousOrNormal(PermissionInfo permissionInfo) {
        switch (permissionInfo.protectionLevel & PermissionInfo.PROTECTION_MASK_BASE) {
            case PermissionInfo.PROTECTION_DANGEROUS:
                return true;
            case PermissionInfo.PROTECTION_NORMAL:
                return true;
            case PermissionInfo.PROTECTION_SIGNATURE:
                return false;
            case PermissionInfo.PROTECTION_SIGNATURE_OR_SYSTEM:
                return false;
            default:
                return true;
        }
    }

    public static boolean isDangerousOrNormal(String permission) {
        if (TextUtils.isEmpty(permission)) {
            return true;
        }
        try {
            PackageManager pm = AtEnvironment.getPackageManager();
            return isDangerousOrNormal(pm.getPermissionInfo(permission, -1));
        } catch (PackageManager.NameNotFoundException e) {
            // e.printStackTrace();
        }
        return true;
    }
}

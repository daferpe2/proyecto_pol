
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.operations.autentiacion_funciones import get_current_user_id
from models import EstadosValidacion, Rol, UserTable


def check_roles(user:UserTable):
    if user.rol not in [Rol.qc, Rol.qc_s, Rol.analista, Rol.jefe, Rol.super_admin]:
        return RedirectResponse(url="/",status_code=status.HTTP_302_FOUND)


def require_role(roles_permitidos: list[Rol]):
    def dependency(user: UserTable = Depends(get_current_user_id)):
        if user.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol no autorizado para esta ruta"
            )
        return user
    return dependency




# # Roles para ver

# def require_can_view(
#     rdp: RDPTable,
#     user: UserTable = Depends(get_current_user_id),
# ):

#     # REGISTRO: solo sus propios RDP
#     if user.rol == Rol.registro:
#         if rdp.creado_por != user.id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Registrador solo puede ver sus propios RDP"
#             )
#         return user

#     # QC / QC_S: región o comisión
#     if user.rol in [Rol.qc, Rol.qc_s]:
#         if rdp.regional not in [user.regional, user.regional_comision]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="QC/QC_S solo pueden ver RDP de su región o comisión"
#             )
#         return user

#     # ANALISTA: solo su región
#     if user.rol == Rol.analista:
#         if rdp.regional != user.regional:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Analista solo puede ver RDP de su región"
#             )
#         return user

#     # JEFE: solo su región (si luego decides que es nacional, se cambia)
#     if user.rol == Rol.jefe:
#         if rdp.regional != user.regional:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Jefe solo puede ver RDP de su región"
#             )
#         return user

#     # SUPER_ADMIN: ve todo
#     if user.rol == Rol.super_admin:
#         return user

#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Usuario no autorizado para ver este RDP"
#     )


# # Roles para editar:

# def require_can_edit(
#     rdp: RDPTable,
#     user: UserTable = Depends(get_current_user_id),
# ):

#     # REGISTRO: solo sus RDP y solo pendiente/observado
#     if user.rol == Rol.registro:
#         if rdp.creado_por != user.id or \
#            rdp.estado not in [EstadosValidacion.PENDIENTE, EstadosValidacion.OBSERVADO]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Registrador solo puede editar RDP pendientes/observados"
#             )
#         return user

#     # QC: pendiente/observado y región/comisión
#     if user.rol == Rol.qc:
#         if rdp.estado not in [EstadosValidacion.PENDIENTE, EstadosValidacion.OBSERVADO] or \
#            rdp.regional not in [user.regional, user.regional_comision]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="QC solo puede editar RDP pendientes/observados de su región/comisión"
#             )
#         return user

#     # QC_S: siempre que región/comisión coincida
#     if user.rol == Rol.qc_s:
#         if rdp.regional not in [user.regional, user.regional_comision]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="QC_S solo puede editar RDP de su región/comisión"
#             )
#         return user

#     # SUPER_ADMIN: siempre
#     if user.rol == Rol.super_admin:
#         return user

#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Este rol no puede editar RDP"
#     )



# # roles de auditar

# def require_can_audit(
#     rdp: RDPTable,
#     user: UserTable = Depends(get_current_user_id),
# ):

#     # QC: solo pendiente/observado y región/comisión
#     if user.rol == Rol.qc:
#         if rdp.estado not in [EstadosValidacion.PENDIENTE, EstadosValidacion.OBSERVADO] or \
#            rdp.regional not in [user.regional, user.regional_comision]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="QC solo puede auditar RDP pendientes/observados de su región/comisión"
#             )
#         return user

#     # QC_S: cualquier estado, región/comisión
#     if user.rol == Rol.qc_s:
#         if rdp.regional not in [user.regional, user.regional_comision]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="QC_S solo puede auditar RDP de su región/comisión"
#             )
#         return user

#     # SUPER_ADMIN: siempre
#     if user.rol == Rol.super_admin:
#         return user

#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Este rol no puede auditar RDP"
#     )



# # Roles de revertir

# def require_can_revert(
#     rdp: RDPTable,
#     user: UserTable = Depends(get_current_user_id),
# ):

#     # SUPER_ADMIN: siempre
#     if user.rol == Rol.super_admin:
#         return user

#     # QC_S: solo si hay auditoría previa, estado auditado y región/comisión
#     if user.rol == Rol.qc_s:
#         if not rdp.tiene_auditoria_previa or \
#            rdp.estado not in [
#                EstadosValidacion.APROBADO,
#                EstadosValidacion.RECHAZADO,
#                EstadosValidacion.OBSERVADO
#            ] or \
#            rdp.regional not in [user.regional, user.regional_comision]:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="QC_S solo puede revertir auditorías previas de su región/comisión"
#             )
#         return user

#     raise HTTPException(
#         status_code=status.HTTP_403_FORBIDDEN,
#         detail="Este rol no puede revertir auditorías"
#     )

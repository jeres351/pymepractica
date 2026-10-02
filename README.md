# pymepractica
practica de pyme en poo python

en la terminal poner estos comandos

py -m venv .venv

.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt


poner tus credenciales Y DATOS EN  en .env

BASE DE DATOS EN MYSQL PERO SE PUEDE USAR EN CUALQUIERA


CREATE DATABASE pyme;

USE pyme;

CREATE TABLE direccion (
    id_direccion INT AUTO_INCREMENT,
    numero_lugar VARCHAR(30)  NOT NULL,
    calle        VARCHAR(100) NOT NULL,
    comuna       VARCHAR(100) NOT NULL,
    region       VARCHAR(100) NOT NULL,

    CONSTRAINT pk_direccion 
    PRIMARY KEY (id_direccion)
) COMMENT = 'Tabla para registrar las Direcciones';


CREATE TABLE proveedor (
    rut          VARCHAR(15) NOT NULL,
    nombre       VARCHAR(30),
    correo       VARCHAR(50),
    id_direccion INT NOT NULL,

    CONSTRAINT pk_proveedor 
    PRIMARY KEY (rut),
    
    CONSTRAINT fk_p_direccion
    FOREIGN KEY (id_direccion) REFERENCES direccion(id_direccion)
) COMMENT = 'Esta tabla sirve para que se registre el proveedor';


CREATE TABLE categoria(
    id_categoria          INT AUTO_INCREMENT,
    nombre                VARCHAR(35) NOT NULL,
    descripcion_categoria TEXT NULL,

    CONSTRAINT pk_categoria 
    PRIMARY KEY (id_categoria)
) COMMENT = 'Esta tabla sirve para el registro de las Categorias de los Productos, junto con una descripcion general';

CREATE TABLE producto (
    gtin                 VARCHAR(14),  
    nombre               VARCHAR(50) NOT NULL,
    descripcion_producto TEXT NULL,
    precio_compra        DECIMAL(10,2),
    perecible            TINYINT DEFAULT 0,    

    CONSTRAINT pk_producto 
    PRIMARY KEY (gtin)
) COMMENT = 'Esta tabla es para registrar los Productos. Si es perecible anadir 1, por defecto en 0 (Si no es perecible)';

CREATE TABLE almacen (
    id_almacen     INT AUTO_INCREMENT,
    nombre_almacen VARCHAR(50),
    id_direccion   INT NOT NULL,

    CONSTRAINT pk_almacen
    PRIMARY KEY (id_almacen), 

    CONSTRAINT fk_a_direccion
    FOREIGN KEY (id_direccion) REFERENCES direccion(id_direccion)
) COMMENT = 'Esta tabla es para registrar los Almacenes';

CREATE TABLE ingresos (
    id_ingresos   INT AUTO_INCREMENT,
    gtin_producto VARCHAR(14),
    fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP ,
    cantidad      INT NOT NULL, 
    observacion   TEXT,
    rut_proveedor VARCHAR(15),


CONSTRAINT pk_ingresos 
PRIMARY KEY (id_ingresos),

CONSTRAINT fk_ingresos_productos
FOREIGN KEY (gtin_producto) REFERENCES producto(gtin),

CONSTRAINT fk_ingresos_proveedores
FOREIGN KEY (rut_proveedor) REFERENCES proveedor(rut)
);

CREATE TABLE salida (
    id_salidas     INT AUTO_INCREMENT,
    gtin_producto  VARCHAR(14),
    cantidad       INT NOT NULL,
    fecha_salida   DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo         VARCHAR(255),

    CONSTRAINT pk_salidas
    PRIMARY KEY (id_salidas),


    CONSTRAINT fk_salidas_productos
    FOREIGN KEY (gtin_producto) REFERENCES producto(gtin)
);







CREATE TABLE proveedor_producto(
    rut_proveedor         VARCHAR(15) NOT NULL,
    gtin_producto         VARCHAR(14) NOT NULL,

    CONSTRAINT pk_proveedor_producto 
    PRIMARY KEY (rut_proveedor, gtin_producto),

    CONSTRAINT fk_pp_proveedor 
    FOREIGN KEY (rut_proveedor) REFERENCES proveedor(rut),
    
    CONSTRAINT fk_pp_producto 
    FOREIGN KEY (gtin_producto) REFERENCES producto(gtin)
) COMMENT = 'Esta tabla es para poder saber de que proveedor pertenece cada producto';

CREATE TABLE categoria_producto(
    id_categoria          INT NOT NULL,
    gtin_producto         VARCHAR(14) NOT NULL,

    CONSTRAINT pk_categoria_producto 
    PRIMARY KEY (id_categoria, gtin_producto),

    CONSTRAINT fk_cp_categoria
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria),

    CONSTRAINT fk_cp_producto
    FOREIGN KEY (gtin_producto) REFERENCES producto(gtin)
) COMMENT = 'Esta tabla es para poder saber cuantas Categorias tiene Cada Producto';

CREATE TABLE producto_almacen(
    gtin_producto       VARCHAR(14) NOT NULL,
    id_almacen          INT NOT NULL,
    stock               INT NOT NULL,

    CONSTRAINT pk_producto_almacen
    PRIMARY KEY (gtin_producto, id_almacen),

    CONSTRAINT fk_pa_producto
    FOREIGN KEY (gtin_producto) REFERENCES producto(gtin),

    CONSTRAINT fk_pa_almacen
    FOREIGN KEY (id_almacen) REFERENCES almacen(id_almacen)
) COMMENT = 'Esta tabla es para poder saber cuantos productos esta en cada almacen';


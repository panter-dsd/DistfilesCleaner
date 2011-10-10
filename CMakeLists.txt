set (PROJECT_OUTPUT_NAME distfilescleaner)
project(DistfilesCleaner)

cmake_minimum_required( VERSION 2.6)

INCLUDE(FindQt4)
find_package( Qt4 REQUIRED )
SET(QT_USE_QTSQL 1)
include( ${QT_USE_FILE})
add_definitions(-DUNICODE)

include_directories(
	src
	${CMAKE_CURRENT_BINARY_DIR}
)

################################################################
# src
################################################################

set (src_SRC
src/main.cpp
)

set (src_HEADERS
)

################################################################
# all
################################################################
set(
	SOURCES
	${src_SRC}
)

set(
	HEADERS
	${src_HEADERS}
)

qt4_wrap_cpp( MOC_SOURCES ${HEADERS} )

add_executable( ${PROJECT_OUTPUT_NAME} ${SOURCES} ${MOC_SOURCES})

target_link_libraries( ${PROJECT_OUTPUT_NAME} ${QT_LIBRARIES} )

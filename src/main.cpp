#include <QtCore/QCoreApplication>
#include <QtCore/QTextCodec>
#include <QtCore/QString>
#include <QtCore/QDirIterator>
#include <QtCore/QFile>
#include <QtCore/QTextStream>
#include <QtCore/QVector>
#include <QtCore/QDebug>
#include <QtCore/QRegExp>
#include <QtCore/QVariant>

#include <QtSql/QSqlDatabase>
#include <QtSql/QSqlQuery>
#include <QtSql/QSqlError>

const QString version = "0.0.0.0";

QSet <QString> files;

void loadManifests (const QString &path);
bool loadManifest (const QString &fileName);
void checkDistfiles (const QString &path);

int main (int argc, char **argv)
{
	QTextCodec::setCodecForCStrings (QTextCodec::codecForName ("UTF-8"));

	QCoreApplication app (argc, argv);
	QCoreApplication::addLibraryPath (app.applicationDirPath () + "/plugins/");

	app.setOrganizationDomain ("simicon.com");
	app.setOrganizationName ("Simicon");
	app.setApplicationVersion (version);
	app.setApplicationName ("DistfilesCleaner");

	loadManifests ("/usr/portage");
	loadManifests ("/var/lib/layman");
	checkDistfiles ("/usr/portage/distfiles");

	return 0;//app.exec();
}

bool loadManifest (const QString &fileName)
{
	bool result = true;
	QFile file (fileName);

	if (result = file.open (QIODevice::ReadOnly)) {
		QTextStream stream (&file);

		static const QRegExp re ("DIST (.*) (\\d*) "
								 "RMD160 (.*) "
								 "SHA1 (.*) "
								 "SHA256 (.*)");

		while (result && !stream.atEnd()) {
			const QString str = stream.readLine ();

			if (re.exactMatch (str)) {
				files.insert (re.cap (1));
			}
		}
	}

	return result;
}

void loadManifests (const QString &path)
{
	QDirIterator it (path,
					 QStringList () << "Manifest",
					 QDir::Files,
					 QDirIterator::Subdirectories);

	while (it.hasNext()) {
		it.next();
		qDebug () << "Load " << it.filePath ();

		if (!loadManifest (it.filePath ())) {
			break;
		}
	}
}

void checkDistfiles (const QString &path)
{
	QDirIterator it (path, QDir::Files);

	qint64 totalSize = 0;
	while (it.hasNext()) {
		it.next();

		if (!files.contains (it.fileName ())) {
			totalSize += it.fileInfo().size();
			qDebug () << it.filePath ();
		}
	}

	qDebug () << "Total size " << totalSize;
}

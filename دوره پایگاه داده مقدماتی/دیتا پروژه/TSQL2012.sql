USE [master]
GO

/* For security reasons the login is created disabled and with a random password. */
/****** Object:  Login [##MS_PolicyEventProcessingLogin##]    Script Date: 6/11/2026 3:55:05 AM ******/
CREATE LOGIN [##MS_PolicyEventProcessingLogin##] WITH PASSWORD=N'e4RobJPHRwa7vzts3g+Rwr1fC7HAvzLlgdYDslWWkhs=', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=ON
GO

ALTER LOGIN [##MS_PolicyEventProcessingLogin##] DISABLE
GO


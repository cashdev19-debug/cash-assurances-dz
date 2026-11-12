

# -------------------------------------Getters -----------------------------------------------------------------------


def getTypeHabitation(cr):

    cr.execute(
        "SELECT  [Code_Type_Habitation],[Designation] FROM [EASIC].[dbo].[TYPE_HABITATION] WHERE [existe] = %s",
        [0],
    )
    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))
    return rows


def getQualiteJuridique(cr):

    cr.execute(
        "SELECT  [Code_Qualite_Jurid_Assure],[Designation] FROM [EASIC].[dbo].[QUALITE_JURIDIQ_ASSURE] WHERE [existe] = %s",
        [0],
    )
    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))
    return rows


def getWilaya(cr):
    cr.execute(
        "SELECT  [CODE_DAIRA_WILAYA],    CONCAT(UPPER(SUBSTRING([DAIRA_WILAYA_F], 1, 1)),LOWER(SUBSTRING([DAIRA_WILAYA_F], 2, len([DAIRA_WILAYA_F])))) AS wilaya_capfirst FROM [EASIC].[dbo].[DAIRA_WILAYA] where [TYPE_DAIRA_WILAYA] = '1' and [EXISTE] ='0' and [CODE_ZONE] > 0 ORDER BY [CODE_DAIRA_WILAYA]"
    )
    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))
    return rows


def getCommune(cr,wilaya):
    cr.execute(
        "SELECT  [CODE_COMMUNE],[COMMUNE_F] FROM [EASIC].[dbo].[COMMUNE]  where CODE_WILAYA = %s   ORDER BY [COMMUNE_F]",
        [wilaya],
    )
    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))
    return rows


def getActiviteProfession(cr):
    cr.execute(
        "SELECT  [CODE_ACTIVITE],[ACTIVITE_F] FROM [EASIC].[dbo].[ACTIVITE_PROFESSION] WHERE [existe] = %s ORDER BY [ACTIVITE_F]",
        [0],
    )
    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))
    return rows


def getCodeContrat(cr,CODE_AGENCE, CODE_PRODUIT, ANNEE_CONTRAT):
    cr.execute(
        "SELECT [dbo].[NUM_DEVI5](%s, %s, %s, '10') AS code_contrat",
        (CODE_AGENCE, CODE_PRODUIT, ANNEE_CONTRAT),
    )
    return cr.fetchone()[0]


def getNewCodeClient(cr,CODE_AGENCE):
    cr.execute(
        """
                    SELECT MAX(CODE_CLIENT)  AS mx
                    FROM [EASIC].[dbo].[CLIENT]
                    WHERE [CODE_AGENCE] = %s
                    """,
        [CODE_AGENCE],
    )
    row = cr.fetchone()
    max_code = row[0] if row[0] else 0
    return str(int(max_code) + 1).zfill(6)


def getClient(cr,code_client, CODE_AGENCE):
    cr.execute(
        """    
                    select 
                    c.NOM_CLIENT AS Client_Last_Name,
                    c.PRENOM_CLIENT AS Client_First_Name,
                    a.ADRESSE_A AS Address_Line1,

                    t.TEL_FAX_MAIL AS Phone_Or_Email,
                    c.[TITRE_CLIENT] , c.[CODE_CLIENT]
                    FROM 
                    [EASIC].[dbo].[CLIENT] c
                    INNER JOIN [EASIC].[dbo].[ADRESSE_CLIENT] a ON c.CODE_CLIENT = a.CODE_CLIENT and c.CODE_AGENCE=a.CODE_AGENCE and c.CODE_AGENCE=%s
                    LEFT JOIN [EASIC].[dbo].[TEL_FAX_MAIL] t ON c.CODE_CLIENT = t.CODE_CLIENT and     c.CODE_AGENCE=t.CODE_AGENCE and c.CODE_AGENCE=%s
   
                     where  c.[CODE_CLIENT] =%s
                    """,
        [CODE_AGENCE, CODE_AGENCE, code_client],
    )

    return cr.fetchone()


def getProducts(cr,CODE_PRODUIT, TYPE_PRODUIT, VISIBLE, EXISTE):
    cr.execute(
        """  SELECT     CODE_PRODUIT, L_Produit, Abrege, TYPE_PRODUIT, DEPEND_DE, VTA, LIMITE,
                        FRANCHISE, Reduction_Possible, Majoration_Possible, PERIODE_INDEMNISATION,
                        questionnaire, VALVTA, VISIBLE, EXISTE, Res_Princ_REP, 
                         Res_Nono_REP, Res_Princ_GR, Res_Nono_GR, CONCERNE_VERSION, FAMILLE
                    FROM            dbo.PRODUIT
                WHERE        (CODE_PRODUIT LIKE %s) AND (TYPE_PRODUIT = %s) AND (VISIBLE = %s) AND (EXISTE = %s)
                        """,
        (CODE_PRODUIT, TYPE_PRODUIT, VISIBLE, EXISTE),
    )
    return cr.fetchall()


def getCodeClient(cr,identifiant):
    cr.execute(
        """
                    SELECT         [CODE_CLIENT] 
                        FROM       [EASIC].[dbo].[CLIENT] WHERE identifiant=%s 
                                        """,
        [identifiant],
    )
    return cr.fetchone()[0]


def getMhTarifIncendie(cr,superficie, valeur_contenu, type_habitation):
    cr.execute(
        """
                    SELECT        min(Proprietaire),min(Locataire) 
                        FROM            MH_TARIF_INCENDIE  where  
                                      SUPERFICIE_MIN <= %s and   SUPERFICIE_MAX >= %s and  CAPITAL_MOBILIER >= %s   and Code_Type_Habitation=%s 
                                        """,
        (superficie, superficie, valeur_contenu, type_habitation),
    )
    return cr.fetchone()


def getCodeContratsObjetGarantie(
   cr, CODE_CONTRAT, CODE_PRODUIT, CODE_AGENCE, ANNEE_CONTRAT, TYPE_CONTRAT
):
    cr.execute(
        """ select  CODE_GARANTIE    FROM [EASIC].[dbo].[CONTRATS_OBJETS_GARANTIES]   WHERE 
                CODE_CONTRAT = %s AND CODE_PRODUIT = %s  AND CODE_AGENCE = %s  AND ANNEE_CONTRAT = %s  AND TYPE_CONTRAT = %s
                """,
        (CODE_CONTRAT, CODE_PRODUIT, CODE_AGENCE, ANNEE_CONTRAT, TYPE_CONTRAT),
    )
    return cr.fetchall()


def getMajorationReduction(cr,reduction):
    cr.execute(
        """ select  APPLICABLE,VALEUR,RED_MAJ,VALEUR_TAUX from  [EASIC].[dbo].[MAJORATION_REDUCTION] where 
                  CODE_RED_MAJ = %s   
                           """,
        (reduction),
    )
    return cr.fetchone()


def getPrimeNette(
    cr,
    CODE_AGENCE,
    CODE_PRODUIT,
    CODE_CONTRAT,
    ANNEE_CONTRAT,
    TYPE_CONTRAT,
):

    cr.execute(
        """    
                    SELECT 
                   [PRIME],[TAXES],[COUT_POLICE],[TIMBRE_DIMENSION]
                    FROM 
                    [EASIC].[dbo].[CONTRAT_TOTAL] 
                     WHERE CODE_AGENCE = %s and CODE_PRODUIT = %s and CODE_CONTRAT = %s and ANNEE_CONTRAT = %s and TYPE_CONTRAT = %s 
                    """,
        (CODE_AGENCE, CODE_PRODUIT, CODE_CONTRAT, ANNEE_CONTRAT, TYPE_CONTRAT),
    )

    return cr.fetchone()


def getCodeProduit(cr,CODE_PRODUIT, TYPE_PRODUIT):
    cr.execute(
        """ select CODE_PRODUIT, L_Produit from  [EASIC].[dbo].[PRODUIT] 
                       where (CODE_PRODUIT LIKE %s) and TYPE_PRODUIT= %s  """,
        (CODE_PRODUIT, TYPE_PRODUIT),
    )

    return cr.fetchall()


def getPrimes(cr,CODE_AGENCE, ANNEE_CONTRAT, CODE_PRODUIT, CODE_CONTRAT):

    cr.execute(
        """DECLARE @LesTxPrime VARCHAR(1024),@LesPrimes VARCHAR(1024),@CHAINE_PRIME VARCHAR(1024), @LesVTA VARCHAR(1024), @LesLimite VARCHAR(1024),
            @LesFranchises VARCHAR(1024),@RESULTAT INT,@M_RESULTAT INT;

            -- Initialize output parameters
            SET @LesTxPrime = '';SET @LesPrimes = '';SET @CHAINE_PRIME = '';SET @LesVTA = '';SET @LesLimite = '';SET @LesFranchises = '';SET @RESULTAT = 0;SET @M_RESULTAT = 0;

            -- Execute the stored procedure
            EXEC [dbo].[TARIF_CAT_NAT]    @CODE_AGENCE = %s, @ANNEE_CONTRAT = %s,  @TYPE_CONTRAT = '10',  @CODE_PRODUIT = %s,  @CODE_CONTRAT = %s,
            @NUMERO = '00001',    @TYPE_OBJET = '4000', @LISTE_GARANTIES = '1213AA#1213AB#', @LesTxPrime = @LesTxPrime OUTPUT, @LesPrimes = @LesPrimes OUTPUT,
            @CHAINE_PRIME = @CHAINE_PRIME OUTPUT,  @LesVTA = @LesVTA OUTPUT,   @LesLimite = @LesLimite OUTPUT,  @LesFranchises = @LesFranchises OUTPUT,
            @RESULTAT = @RESULTAT OUTPUT, @M_RESULTAT = @M_RESULTAT OUTPUT;

            -- Check output values 
            SELECT   @LesTxPrime AS LesTxPrime,  @LesPrimes AS LesPrimes, @CHAINE_PRIME AS ChainePrime,  @LesVTA AS LesVTA,  @LesLimite AS LesLimite,
            @LesFranchises AS LesFranchises,  @RESULTAT AS Resultat,  @M_RESULTAT AS MResultat;

                        """,
        (CODE_AGENCE, ANNEE_CONTRAT, CODE_PRODUIT, CODE_CONTRAT),
    )

    return cr.fetchone()


# *****************************************************************************************************************************


def getZoneCirculation(cr,wilaya):
    cr.execute(
        """SELECT [CODE_ZONE] 
                      FROM [EASIC].[dbo].[DAIRA_WILAYA]
                      WHERE TYPE_DAIRA_WILAYA = '1' AND EXISTE='0' AND CODE_DAIRA_WILAYA = %s
                   """,
        [wilaya],
    )

    return cr.fetchone()[0]


def getCodeZone(cr,commune):
    cr.execute(
        """SELECT [ZONE_SISMIQUE] 
                      FROM [EASIC].[dbo].[COMMUNE]
                      WHERE [CODE_COMMUNE] = %s AND [EXISTE] = '0'
                   """,
        [commune],
    )

    return cr.fetchone()[0]


def getTarifCatnat(cr,CODE_PRODUIT, ASPECT_SISMIQUE, ZONE):
    cr.execute(
        """SELECT [Taux] 
                      FROM [EASIC].[dbo].[TARIF_CATNAT] 
                      WHERE [NUM_TARIF]='003' AND [CODE_PRODUIT] = %s AND [ASPECT_SISMIQUE] = %s AND [ZONE] = %s
                   """,
        (CODE_PRODUIT, ASPECT_SISMIQUE, ZONE),
    )

    return cr.fetchone()[0]


def getTarifnormatif(cr,code_zone):
    cr.execute(
        """SELECT [LOG_INDIV], [LOG_COLL] 
                  FROM [EASIC].[dbo].[TARIFNORMATIF]  
                  WHERE [NUM_TARIF]='003' AND [ZONE]=%s
               """,
        (code_zone,),
    )
    return cr.fetchone()


# ----------------------------------------------------------
def getTypeVehicule(cr,code_type):
    cr.execute(
        """SELECT [CODE_TYPE_GENRE], [TYPE_F] 
                  FROM [EASIC].[dbo].[TYPE_GENRE_AUTO]
                  WHERE [EXISTE]='0' AND [CODE_TYPE_GENRE] =%s
               """,
        [code_type],
    )

    rows = cr.fetchone()
    rows = [("", "--------------"), (rows)]
    return rows


def getGenreVehicule(cr,typevehicule):
    cr.execute(
        """ select [CODE_GENRE], [GENRE_F] from  [EASIC].[dbo].[GENRE_AUTO] 
                       where TYPE_GENRE= %s  """,
        (typevehicule),
    )
    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))
    return rows


def getUsageVehicule(cr,typeVehicule):
    cr.execute(
        """SELECT g.CODE, g.USAGE_L 
                  FROM [EASIC].[dbo].[AUTO_GENRE_USAGE] u 
                  INNER JOIN [EASIC].[dbo].[USAGE_VHICULE]  g on g.CODE = u.Code_usage 
                  WHERE u.EXISTE='0' AND u.code_Genre =%s
               """,
        (typeVehicule,)
    )

    rows = cr.fetchall()
    rows.insert(0, ("", "--------------"))

    return rows


# *****************************************************************************************************************************

# --------------------------------------- insertions ------------------------------------------------------------------------


def insertContrat(
    cr,
    CODE_AGENCE,
    produit,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    NB_OBJET,
    R_CODE_PRODUIT,
    R_ANNEE_CONTRAT,
    R_CODE_CONTRAT,
    R_TYPE_CONTRAT,
    DATE_SAISIE,
    DATE_SOUSCRIPTION,
    DATE_EFFET,
    DATE_ECHEANCE,
    DUREE,
    COUT_POLICE,
    AUTRE_FRAIS,
    TIMBRE_DIMENSION,
    CLOTURER,
    OBSERVATION,
    APPOTEUR,
    existe,
    AGENCE_GESTIONNAIRE,
    EXONERE,
    DEVISE_CONTRAT,
    TYPE_AVENANT,
    CODE_REGISTRE,
    ANNEE_REGISTRE,
    AGENCE_REGISTRE,
    NUM_PAGE,
    NUM_LIGNE,
    VTA_LIMITE,
    FRANCHISE,
    LIMITE,
    USER,
    NEWAGENCE,
    SITUATION,
    ENCAISSEMENT,
    REPONSE_CLIENT,
    CODE_PRODUIT_AFFICHE,
    AGENCE_GESTIONNAIRE_SAVE,
):
    print("insertContrat")
    return cr.execute(
        """
                INSERT INTO [EASIC].[dbo].[CONTRATS] (
                    [CODE_AGENCE], [CODE_PRODUIT], [ANNEE_CONTRAT], [CODE_CONTRAT], [TYPE_CONTRAT], [NB_OBJET],
                    [R_CODE_AGENCE], [R_CODE_PRODUIT], [R_ANNEE_CONTRAT], [R_CODE_CONTRAT], [R_TYPE_CONTRAT],
                    [DATE_SAISIE], [DATE_SOUSCRIPTION], [DATE_EFFET], [DATE_ECHEANCE], [DUREE], [COUT_POLICE],
                    [AUTRE_FRAIS], [TIMBRE_DIMENSION], [CLOTURER], [OBSERVATION], [APPOTEUR], [existe],
                    [AGENCE_GESTIONNAIRE], [EXONERE], [DEVISE_CONTRAT], [TYPE_AVENANT], [CODE_REGISTRE],
                    [ANNEE_REGISTRE], [AGENCE_REGISTRE], [NUM_PAGE], [NUM_LIGNE], [VTA_LIMITE], [FRANCHISE],
                    [LIMITE], [USER], [NEWAGENCE], [SITUATION], [ENCAISSEMENT], [REPONSE_CLIENT], 
                    [CODE_PRODUIT_AFFICHE], [AGENCE_GESTIONNAIRE_SAVE]
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """,
        (
            CODE_AGENCE,
            produit,
            ANNEE_CONTRAT,
            CODE_CONTRAT,
            TYPE_CONTRAT,
            NB_OBJET,
            CODE_AGENCE,
            R_CODE_PRODUIT,
            R_ANNEE_CONTRAT,
            R_CODE_CONTRAT,
            R_TYPE_CONTRAT,
            DATE_SAISIE,
            DATE_SOUSCRIPTION,
            DATE_EFFET,
            DATE_ECHEANCE,
            DUREE,
            COUT_POLICE,
            AUTRE_FRAIS,
            TIMBRE_DIMENSION,
            CLOTURER,
            OBSERVATION,
            APPOTEUR,
            existe,
            AGENCE_GESTIONNAIRE,
            EXONERE,
            DEVISE_CONTRAT,
            TYPE_AVENANT,
            CODE_REGISTRE,
            ANNEE_REGISTRE,
            AGENCE_REGISTRE,
            NUM_PAGE,
            NUM_LIGNE,
            VTA_LIMITE,
            FRANCHISE,
            LIMITE,
            USER,
            NEWAGENCE,
            SITUATION,
            ENCAISSEMENT,
            REPONSE_CLIENT,
            CODE_PRODUIT_AFFICHE,
            AGENCE_GESTIONNAIRE_SAVE,
        ),
    )


def insertContratsObjet(
    cr,
    CODE_AGENCE,
    produit,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    numero,
    type_objet,
    DETAIL_OBJET,
    questionnaire,
    VTA_LIMITE,
    FRANCHISE,
    LIMITE,
):
    print("insertContratsObjet")
    return cr.execute(
        """ insert into  [EASIC].[dbo].[CONTRATS_OBJETS] ( 
            [CODE_AGENCE] ,[CODE_PRODUIT],[ANNEE_CONTRAT],[CODE_CONTRAT],[TYPE_CONTRAT],[NUMERO]
            ,[TYPE_OBJET],[DETAIL_OBJET],[questionnaire],[VTA_LIMITE]
            ,[FRANCHISE],[LIMITE]  ) 
                       values (    
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                       ) 

            
   
            """,
        (
            CODE_AGENCE,
            produit,
            ANNEE_CONTRAT,
            CODE_CONTRAT,
            TYPE_CONTRAT,
            numero,
            type_objet,
            DETAIL_OBJET,
            questionnaire,
            VTA_LIMITE,
            FRANCHISE,
            LIMITE,
        ),
    )


def insertClient(cr,CODE_AGENCE, new_code, nom, prenom, titre, identifiant, adressec, tfe):
    cr.execute(
        """
                        INSERT INTO [EASIC].[dbo].[CLIENT] (
                        [CODE_AGENCE],
                        [CODE_CLIENT],
                        [NOM_CLIENT],
                        [PRENOM_CLIENT],
                        [TITRE_CLIENT],
                          [identifiant]    
                        ) VALUES (%s, %s, %s, %s, %s,%s)
                        """,
        [CODE_AGENCE, new_code, nom, prenom, titre, identifiant],
    )

    cr.execute(
        """
                        INSERT INTO [EASIC].[dbo].[ADRESSE_CLIENT] (
                        [CODE_AGENCE],
                        [CODE_CLIENT],
                        [CODE_ADRESSE],
                        [ADRESSE_A] ,
                        [CODEPOSTAL],
                        [NATURE_ADRESSE]
              
                         ) VALUES (%s, %s,'1', %s,'0','Bureau')
                        """,
        [CODE_AGENCE, new_code, adressec],
    )

    cr.execute(
        """
                        INSERT INTO [EASIC].[dbo].[TEL_FAX_MAIL] (
                        [CODE_AGENCE],
                        [CODE_CLIENT],
                        [CODE_TEL_FAX],
                        [TEL_FAX_MAIL]
              
                        ) VALUES (%s, %s,'1', %s)
                         """,
        [CODE_AGENCE, new_code, tfe],
    )
    print("insertClient")


def insertSouscripteur(
    cr,
    CODE_AGENCE,
    produit,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    CODE_CLIENT,
    NOM_CLIENT,
    PRENOM_CLIENT,
    TITRE_CLIENT,
    TYPE_CLIENT,
    ACTIVITE_CLIENT,
    DATNAIS,
    COMMUNENAIS,
    SEXE,
    NOMA,
    PRENOMA,
    ADRESSE,
    TEL,
    Exporte,
    NOM_CLIENT_ORIGINAL,
    PRENOM_CLIENT_ORIGINAL,
):
    cr.execute(
        """ 
                    INSERT INTO [EASIC].[dbo].[SOUSCRIPTEUR] (
                    [CODE_AGENCE_CONTRAT], [CODE_PRODUIT], [ANNEE_CONTRAT], [CODE_CONTRAT], [TYPE_CONTRAT],
                    [CODE_AGENCE], [CODE_CLIENT], [NOM_CLIENT], [PRENOM_CLIENT], [TITRE_CLIENT], [TYPE_CLIENT], [ACTIVITE_CLIENT],
                    [DATNAIS], [COMMUNENAIS], [SEXE], [NOMA], [PRENOMA], [ADRESSE], [TEL], [Exporte], [NOM_CLIENT_ORIGINAL], [PRENOM_CLIENT_ORIGINAL]
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
        (
            CODE_AGENCE,
            produit,
            ANNEE_CONTRAT,
            CODE_CONTRAT,
            TYPE_CONTRAT,
            CODE_AGENCE,
            CODE_CLIENT,
            NOM_CLIENT,
            PRENOM_CLIENT,
            TITRE_CLIENT,
            TYPE_CLIENT,
            ACTIVITE_CLIENT,
            DATNAIS,
            COMMUNENAIS,
            SEXE,
            NOMA,
            PRENOMA,
            ADRESSE,
            TEL,
            Exporte,
            NOM_CLIENT_ORIGINAL,
            PRENOM_CLIENT_ORIGINAL,
        ),
    )
    print("inserSouscripteur")


def insertBeneficier(
    cr,
    CODE_AGENCE_CONTRAT,
    CODE_PRODUIT,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    CODE_CLIENT,
    NOM_CLIENT,
    PRENOM_CLIENT,
    TITRE_CLIENT,
    TYPE_CLIENT,
    ACTIVITE_CLIENT,
    DATNAIS,
    COMMUNENAIS,
    SEXE,
    NOMA,
    PRENOMA,
    ADRESSE,
    TEL,
    Exporte,
    NUMERO,
):
    cr.execute(
        """ 
                    INSERT INTO [EASIC].[dbo].[BENEFICIER] (
                    [CODE_AGENCE_CONTRAT] ,[CODE_PRODUIT] ,[ANNEE_CONTRAT] ,[CODE_CONTRAT] ,[TYPE_CONTRAT],[CODE_AGENCE]
                    ,[CODE_CLIENT],[NOM_CLIENT],[PRENOM_CLIENT],[TITRE_CLIENT],[TYPE_CLIENT],[ACTIVITE_CLIENT],[DATNAIS]
                    ,[COMMUNENAIS],[SEXE],[NOMA],[PRENOMA],[ADRESSE],[TEL],[Exporte],[NUMERO]
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
        (
            CODE_AGENCE_CONTRAT,
            CODE_PRODUIT,
            ANNEE_CONTRAT,
            CODE_CONTRAT,
            TYPE_CONTRAT,
            CODE_AGENCE_CONTRAT,
            CODE_CLIENT,
            NOM_CLIENT,
            PRENOM_CLIENT,
            TITRE_CLIENT,
            TYPE_CLIENT,
            ACTIVITE_CLIENT,
            DATNAIS,
            COMMUNENAIS,
            SEXE,
            NOMA,
            PRENOMA,
            ADRESSE,
            TEL,
            Exporte,
            NUMERO,
        ),
    )

    print("insertBeneficier")


def insertContratsObjetHabitation(
    cr,
    CODE_AGENCE,
    CODE_PRODUIT,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    NUMERO,
    TYPE_OBJET,
    QUALITE_JURID_ASSURE,
    TYPE_HABITATION,
    ADRESSE,
    COMMUNE,
    WILAYA,
    NB_PIECE,
    SUPERFICIE,
    VALEUR_CONTENU,
    VALEUR_OBJETS_DE_VALEUR,
    SYSTEME_PROTECTION,
    TERASSE_BALCON,
    OCCUPATION_RISQUE_PROFESSIONNEL,
    ACTIVITE_RISQUE_PROFESSIONNEL,
    INNOCUPATION,
    SEMI_LEGER_PLUS_90,
    VTA_LIMITE,
    LIMITE,
    intoxication_alimentaire,
    tempete,
):
    cr.execute(
        """ insert into  [EASIC].[dbo].[CONTRATS_OBJETS_HABITATION] (
            [CODE_AGENCE],[CODE_PRODUIT],[ANNEE_CONTRAT] ,[CODE_CONTRAT],[TYPE_CONTRAT],
            [NUMERO]  ,[TYPE_OBJET],[QUALITE_JURID_ASSURE]  ,[TYPE_HABITATION],[ADRESSE]
            ,[COMMUNE],[WILAYA],[NB_PIECE] ,[SUPERFICIE] ,[VALEUR_CONTENU] ,[VALEUR_OBJETS_DE_VALEUR]
            ,[SYSTEME_PROTECTION] ,[TERASSE_BALCON],[OCCUPATION_RISQUE_PROFESSIONNEL],[ACTIVITE_RISQUE_PROFESSIONNEL]
            ,[INNOCUPATION],[SEMI_LEGER_PLUS_90],[VTA_LIMITE],[LIMITE],[intoxication_alimentaire],[tempete] ) 
            values (    
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )  

            
   
            """,
        (
            CODE_AGENCE,
            CODE_PRODUIT,
            ANNEE_CONTRAT,
            CODE_CONTRAT,
            TYPE_CONTRAT,
            NUMERO,
            TYPE_OBJET,
            QUALITE_JURID_ASSURE,
            TYPE_HABITATION,
            ADRESSE,
            COMMUNE,
            WILAYA,
            NB_PIECE,
            SUPERFICIE,
            VALEUR_CONTENU,
            VALEUR_OBJETS_DE_VALEUR,
            SYSTEME_PROTECTION,
            TERASSE_BALCON,
            OCCUPATION_RISQUE_PROFESSIONNEL,
            ACTIVITE_RISQUE_PROFESSIONNEL,
            INNOCUPATION,
            SEMI_LEGER_PLUS_90,
            VTA_LIMITE,
            LIMITE,
            intoxication_alimentaire,
            tempete,
        ),
    )

    print("insertContratsObjetHabitation")


def insertContratsObjetGaraties(
    cr,
    CODE_AGENCE,
    CODE_PRODUIT,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    NUMERO,
    CODE_GARANTIE,
    PRIME,
    VTA_LIMITE,
    Franchise,
    LIB_GARANTIE,
    LIMITE,
):
    cr.execute(
        """ insert into  [EASIC].[dbo].[CONTRATS_OBJETS_GARANTIES] ([CODE_AGENCE] ,[CODE_PRODUIT]
             ,[ANNEE_CONTRAT],[CODE_CONTRAT] ,[TYPE_CONTRAT],[NUMERO] ,[CODE_GARANTIE] ,[PRIME] ,[VTA_LIMITE] ,[Franchise] ,[LIB_GARANTIE] ,[LIMITE] )
                                values (  %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
                               """,
        (
            CODE_AGENCE,
            CODE_PRODUIT,
            ANNEE_CONTRAT,
            CODE_CONTRAT,
            TYPE_CONTRAT,
            NUMERO,
            CODE_GARANTIE,
            PRIME,
            VTA_LIMITE,
            Franchise,
            LIB_GARANTIE,
            LIMITE,
        ),
    )
    print("insertContratsObjetGaraties")


def insertContratsObjetGarantieRedMaj(
    cr,
    CODE_AGENCE,
    CODE_PRODUIT,
    ANNEE_CONTRAT,
    CODE_CONTRAT,
    TYPE_CONTRAT,
    CODE_GARANTIE,
    NUMERO,
    NUM_RED_MAJ,
    VALEUR,
    VAL_TAUX,
    REDUC_MAJ,
    NOTES,
    Ordre_Application,
    Observation,
):
    strquery = f"""
                        INSERT INTO EASIC.dbo.CONTRATS_OBJETS_GARANTIES_RED_MAJ
                        (CODE_AGENCE, CODE_PRODUIT, ANNEE_CONTRAT, CODE_CONTRAT, TYPE_CONTRAT,
                        CODE_GARANTIE, NUMERO, NUM_RED_MAJ, VALEUR, VAL_TAUX, REDUC_MAJ, NOTES,
                        Ordre_Application, Observation)
                        VALUES (
                            '{CODE_AGENCE}',
                            '{CODE_PRODUIT}',
                            '{ANNEE_CONTRAT}',
                            '{CODE_CONTRAT}',
                            '{TYPE_CONTRAT}',
                            '{CODE_GARANTIE}',
                            '{NUMERO}',
                            '{NUM_RED_MAJ}',
                            '{VALEUR}',
                            '{VAL_TAUX}',
                            '{REDUC_MAJ}',
                            '{NOTES}',
                            {Ordre_Application},
                            '{Observation}'
                        )
                    """
    cr.execute(strquery)
    print("insertContratsObjetGarantieRedMaj")


# --------------- verif  ----------------------------
def existeClient(cr,identifiant):
    cr.execute(
        "select  count(*) as ct   FROM [EASIC].[dbo].[CLIENT] WHERE identifiant= %s",
        [identifiant],
    )
    result = cr.fetchone()[0]
    return result
